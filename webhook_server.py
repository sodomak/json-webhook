#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import argparse
import sys


class WebhookHandler(BaseHTTPRequestHandler):
    silent = False  # Class-level variable to store the --silent flag
    plain = False   # Class-level variable to store the --plain flag
    filters = []    # Class-level variable to store filters

    def log_message(self, format, *args):
        # Suppress HTTP server log lines unless --silent is not set
        if not WebhookHandler.silent:
            super().log_message(format, *args)

    def parse_multiple_json_objects(self, data):
        """
        Parse multiple JSON objects from a string.
        """
        objects = []
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(data):
            try:
                obj, pos = decoder.raw_decode(data, pos)
                objects.append(obj)
            except json.JSONDecodeError:
                break
            while pos < len(data) and data[pos].isspace():
                pos += 1
        return objects

    def extract_filtered_data(self, payload, filters):
        """
        Extract filtered data based on the filters provided.
        Handles both flat and nested structures.
        """
        values = []
        for path in filters:
            keys = path.split(".")
            value = payload
            try:
                for key in keys:
                    if isinstance(value, list):
                        # Handle lists: Extract key from each item
                        value = [item.get(key, None) for item in value if isinstance(item, dict)]
                    elif isinstance(value, dict):
                        value = value.get(key, None)
                    else:
                        value = None  # Stop if a non-dict/list value is encountered
                if value is not None:  # Add non-null values to the result
                    values.append(value)
            except Exception:
                pass
        return values

    def do_POST(self):
        # Read the payload
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Parse multiple JSON objects from the payload
        json_objects = self.parse_multiple_json_objects(post_data)

        # Process and filter each JSON object
        results = []
        for payload in json_objects:
            results.extend(self.extract_filtered_data(payload, WebhookHandler.filters))

        # Handle empty results
        if not results:
            result = None  # Return None or an empty structure if no matches
        else:
            # Simplify the output for single results
            result = results if len(results) > 1 else results[0]

        # Display the result
        if WebhookHandler.plain:
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=4))

        # Respond with 200 OK
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))


def run(ip, port, silent, plain, filters):
    server_address = (ip, port)
    WebhookHandler.silent = silent  # Pass the --silent flag to the handler
    WebhookHandler.plain = plain    # Pass the --plain flag to the handler
    WebhookHandler.filters = filters  # Pass the filters to the handler
    if not silent:
        print(f"Starting server on {ip}:{port}")
    httpd = HTTPServer(server_address, WebhookHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Webhook Server")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP address to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--silent", "-s", action="store_true", help="Display payload only, suppress all other output")
    parser.add_argument("--plain", "-p", action="store_true", help="Output raw JSON payload without formatting")
    parser.add_argument("--filter", "-f", type=str, help="Comma-separated list of JSON paths to filter (e.g., 'key1,key2.subkey')")
    args = parser.parse_args()

    # Parse filters as a list
    filters = args.filter.split(",") if args.filter else []

    try:
        run(args.ip, args.port, args.silent, args.plain, filters)
    except KeyboardInterrupt:
        if not args.silent:
            print("\nServer stopped.")
        sys.exit(0)
