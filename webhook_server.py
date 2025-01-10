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

    def do_POST(self):
        # Read the payload
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data)
        except json.JSONDecodeError:
            payload = {"error": "Invalid JSON payload"}

        # Apply filtering if specified
        if WebhookHandler.filters:
            filtered_payload = {}
            for path in WebhookHandler.filters:
                keys = path.split(".")
                value = payload
                try:
                    for key in keys:
                        if isinstance(value, list):
                            value = [item.get(key, None) for item in value]
                        else:
                            value = value.get(key, None)
                    filtered_payload[path] = value
                except Exception as e:
                    filtered_payload[path] = f"Error: {e}"
            payload = filtered_payload

        # Display the payload
        if WebhookHandler.plain:
            print(json.dumps(payload))
        else:
            print(json.dumps(payload, indent=4))

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
