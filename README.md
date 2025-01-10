
# Webhook Server

A simple Python-based webhook server for testing and processing JSON payloads. The server can filter specific parts of the JSON, format the output, and suppress logs depending on the command-line arguments provided.

## Features

- Accepts HTTP `POST` requests with JSON payloads.
- Filters specific parts of the JSON payload using dot notation (e.g., `key.subkey`).
- Supports multiple filters with a comma-separated list.
- Configurable output:
  - Pretty-printed JSON (default).
  - Raw JSON (`--plain`).
  - Payload-only mode (`--silent`).
- Lightweight and easy to set up.

## Requirements

- Python 3.7 or later
- `httpie` (for testing, optional)

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/webhook-server.git
    cd webhook-server
    ```

2. Make the script executable:
    ```bash
    chmod +x webhook_server.py
    ```

## Usage

Run the server with the desired options:

```bash
./webhook_server.py [--ip <IP_ADDRESS>] [--port <PORT>] [--silent] [--plain] [--filter <FILTERS>]
```

### Options

| Option         | Description                                                                                 |
|----------------|---------------------------------------------------------------------------------------------|
| `--ip`         | IP address to bind the server (default: `0.0.0.0`).                                         |
| `--port`       | Port to bind the server (default: `8080`).                                                  |
| `--silent, -s` | Suppress all output except the payload.                                                     |
| `--plain, -p`  | Output raw JSON payload without formatting.                                                 |
| `--filter, -f` | Comma-separated list of JSON paths to filter (e.g., `key1,key2.subkey`).                    |

### Examples

#### Start the Server

Start the server on `192.168.168.100:3333` in silent mode:

```bash
./webhook_server.py --ip 192.168.168.100 --port 3333 --silent
```

#### Full Payload (No Filters)

Send a POST request using `httpie`:

```bash
http POST http://192.168.168.100:3333 Content-Type:application/json     status="firing" alertname="HighCPU"     details:='{"cpu": "90%", "host": "server1"}'     metadata:='{"severity": "critical", "description": "CPU usage exceeds 90%"}'
```

Expected output:
```json
{
    "status": "firing",
    "alertname": "HighCPU",
    "details": {
        "cpu": "90%",
        "host": "server1"
    },
    "metadata": {
        "severity": "critical",
        "description": "CPU usage exceeds 90%"
    }
}
```

#### Filtered Payload (Multiple Filters)

Run the server with specific filters:

```bash
./webhook_server.py --ip 192.168.168.100 --port 3333 --filter "details.cpu,metadata.severity"
```

Send a POST request:

```bash
http POST http://192.168.168.100:3333 Content-Type:application/json     status="firing" alertname="HighCPU"     details:='{"cpu": "90%", "host": "server1"}'     metadata:='{"severity": "critical", "description": "CPU usage exceeds 90%"}'
```

Expected output:
```json
{
    "details.cpu": "90%",
    "metadata.severity": "critical"
}
```

## License

MIT License
