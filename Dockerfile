FROM python:3.11-slim

# Install Tailscale
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null && \
    curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list && \
    apt-get update && \
    apt-get install -y tailscale && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
