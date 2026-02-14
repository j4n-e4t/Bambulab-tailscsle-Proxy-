# Bambulab Tailscale Proxy

A Docker-based TCP proxy for Bambulab 3D printers with integrated Tailscale support for secure remote access.

## Features

- 🖨️ **Full TCP Proxy**: Transparent TCP proxy to your Bambulab printer in LAN mode
- 🔒 **Tailscale Integration**: Secure remote access to your printer from anywhere
- ⚙️ **Environment-based Configuration**: Easy setup using environment variables
- 🐳 **Docker-based**: Simple deployment with Docker or Docker Compose
- 🔄 **Bidirectional Communication**: Full duplex communication support

## Prerequisites

- Docker and Docker Compose installed
- Bambulab printer with LAN mode enabled
- (Optional) Tailscale account and auth key for remote access

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/j4n-e4t/Bambulab-tailscsle-Proxy-.git
cd Bambulab-tailscsle-Proxy-
```

### 2. Configure Environment Variables

Copy the example environment file and edit it with your settings:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Required configuration:
```bash
PRINTER_HOST=192.168.1.100  # Your printer's IP address
PRINTER_PORT=8883           # Printer port (default: 8883)
```

Optional Tailscale configuration (for remote access):
```bash
TAILSCALE_AUTHKEY=tskey-auth-xxxxx  # Get from https://login.tailscale.com/admin/settings/keys
TAILSCALE_HOSTNAME=bambulab-proxy   # Hostname on your Tailnet
```

### 3. Start the Proxy

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

#### Using Docker

```bash
docker build -t bambulab-proxy .
docker run -d \
  --name bambulab-proxy \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -e PRINTER_HOST=192.168.1.100 \
  -e PRINTER_PORT=8883 \
  -e TAILSCALE_AUTHKEY=tskey-auth-xxxxx \
  -p 8883:8883 \
  bambulab-proxy
```

### 4. Verify the Proxy is Running

```bash
# Check container logs
docker-compose logs -f

# Check Tailscale status (if configured)
docker-compose exec bambulab-proxy tailscale status
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PRINTER_HOST` | Yes | - | IP address of your Bambulab printer |
| `PRINTER_PORT` | No | 8883 | TCP port of the printer |
| `PROXY_BIND_HOST` | No | 0.0.0.0 | Interface to bind the proxy (0.0.0.0 for all) |
| `PROXY_BIND_PORT` | No | 8883 | Local port for the proxy |
| `TAILSCALE_AUTHKEY` | No | - | Tailscale authentication key |
| `TAILSCALE_HOSTNAME` | No | bambulab-proxy | Hostname on Tailscale network |

## Usage

### Local Network Access

Once the proxy is running, you can connect to your printer through the proxy:

- **From the same machine**: `localhost:8883`
- **From other devices on LAN**: `<docker-host-ip>:8883`

### Remote Access via Tailscale

If you've configured Tailscale:

1. Install Tailscale on your remote device
2. Connect to your Tailnet
3. Access the printer using the Tailscale hostname: `bambulab-proxy:8883`

## Troubleshooting

### Check Container Logs

```bash
docker-compose logs -f bambulab-proxy
```

### Test Printer Connectivity

From the Docker host, verify you can reach the printer:

```bash
ping <PRINTER_HOST>
telnet <PRINTER_HOST> 8883
```

### Restart the Proxy

```bash
docker-compose restart
```

### Common Issues

1. **"PRINTER_HOST environment variable is required"**
   - Make sure you've set `PRINTER_HOST` in your `.env` file

2. **Connection refused to printer**
   - Verify printer IP address is correct
   - Ensure printer is in LAN mode
   - Check firewall settings

3. **Tailscale not connecting**
   - Verify `TAILSCALE_AUTHKEY` is valid
   - Check that the container has `NET_ADMIN` and `NET_RAW` capabilities
   - Review Tailscale logs: `docker-compose exec bambulab-proxy tailscale status`

## How It Works

1. **TCP Proxy**: The Python-based proxy listens on the configured port and forwards all TCP traffic to your Bambulab printer
2. **Tailscale**: Creates a secure, encrypted tunnel to access your local network from anywhere
3. **Docker**: Packages everything in a container for easy deployment and isolation

## Security Notes

- Keep your `.env` file secure (it's in `.gitignore` by default)
- Use Tailscale for secure remote access instead of exposing ports directly to the internet
- Rotate Tailscale auth keys periodically
- Consider using ephemeral Tailscale keys for better security

## Development

### Build the Image

```bash
docker build -t bambulab-proxy .
```

### Run Tests

```bash
# Test the proxy without Tailscale
docker run --rm \
  -e PRINTER_HOST=192.168.1.100 \
  -p 8883:8883 \
  bambulab-proxy
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Bambulab for their excellent 3D printers
- Tailscale for making secure networking simple