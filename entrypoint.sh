#!/bin/bash
set -e

echo "Starting Bambulab Printer TCP Proxy with Tailscale"

# Check if Tailscale authentication key is provided
if [ -n "$TAILSCALE_AUTHKEY" ]; then
    echo "Starting Tailscale..."
    
    # Start tailscaled in the background
    tailscaled --tun=userspace-networking --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
    TAILSCALED_PID=$!
    
    # Wait for tailscaled to be ready
    sleep 2
    
    # Authenticate with Tailscale
    echo "Authenticating with Tailscale..."
    tailscale up --authkey="$TAILSCALE_AUTHKEY" --hostname="${TAILSCALE_HOSTNAME:-bambulab-proxy}"
    
    echo "Tailscale started successfully"
    tailscale status
else
    echo "Warning: TAILSCALE_AUTHKEY not set, skipping Tailscale setup"
    echo "The proxy will still work on the local network"
fi

# Start the TCP proxy
echo "Starting TCP proxy..."
exec python3 /app/proxy.py
