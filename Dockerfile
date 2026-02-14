FROM python:3.11-bookworm

# Install basic dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        iptables \
        iproute2 \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Tailscale (using static binary)
# This step is optional - if it fails, the proxy will still work
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    ( wget -q https://pkgs.tailscale.com/stable/tailscale_latest_${ARCH}.tgz -O /tmp/tailscale.tgz && \
      tar xzf /tmp/tailscale.tgz -C /tmp && \
      install -m 755 /tmp/tailscale_*/tailscale /usr/bin/tailscale && \
      install -m 755 /tmp/tailscale_*/tailscaled /usr/sbin/tailscaled && \
      rm -rf /tmp/tailscale* && \
      echo "Tailscale installed successfully" \
    ) || echo "Warning: Tailscale installation skipped - proxy will work without it"

# Create necessary directories
RUN mkdir -p /var/run/tailscale /var/lib/tailscale /app

# Copy application files
COPY proxy.py /app/
COPY entrypoint.sh /app/

# Make scripts executable
RUN chmod +x /app/proxy.py /app/entrypoint.sh

WORKDIR /app

# Expose the default proxy port
EXPOSE 8883

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
