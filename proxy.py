#!/usr/bin/env python3
"""
Simple TCP proxy for Bambulab printers.
Forwards TCP connections from a local port to the printer's IP and port.
"""

import socket
import threading
import sys
import os
import logging
import signal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TCPProxy:
    def __init__(self, local_host, local_port, remote_host, remote_port, buffer_size=4096):
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.buffer_size = buffer_size
        self.server_socket = None
        self.running = False

    def handle_client(self, client_socket, client_address):
        """Handle a single client connection"""
        logger.info(f"New connection from {client_address}")
        
        try:
            # Connect to the remote server (printer)
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_host, self.remote_port))
            logger.info(f"Connected to printer at {self.remote_host}:{self.remote_port}")

            # Start forwarding data in both directions
            def forward(source, destination, direction):
                try:
                    while self.running:
                        data = source.recv(self.buffer_size)
                        if not data:
                            break
                        destination.sendall(data)
                        logger.debug(f"{direction}: {len(data)} bytes")
                except Exception as e:
                    logger.debug(f"Error in {direction}: {e}")
                finally:
                    source.close()
                    destination.close()

            # Create threads for bidirectional forwarding
            client_to_remote = threading.Thread(
                target=forward,
                args=(client_socket, remote_socket, "Client->Printer"),
                daemon=True
            )
            remote_to_client = threading.Thread(
                target=forward,
                args=(remote_socket, client_socket, "Printer->Client"),
                daemon=True
            )

            client_to_remote.start()
            remote_to_client.start()

            # Wait for both threads to complete
            client_to_remote.join()
            remote_to_client.join()

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Connection closed from {client_address}")

    def start(self):
        """Start the TCP proxy server"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.local_host, self.local_port))
            self.server_socket.listen(5)
            logger.info(f"TCP Proxy listening on {self.local_host}:{self.local_port}")
            logger.info(f"Forwarding to {self.remote_host}:{self.remote_port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    break

        except Exception as e:
            logger.error(f"Error starting proxy: {e}")
            sys.exit(1)
        finally:
            self.stop()

    def stop(self):
        """Stop the TCP proxy server"""
        logger.info("Stopping TCP proxy...")
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass


def main():
    # Get configuration from environment variables
    local_host = os.getenv('PROXY_BIND_HOST', '0.0.0.0')
    local_port = int(os.getenv('PROXY_BIND_PORT', '8883'))
    remote_host = os.getenv('PRINTER_HOST')
    remote_port = int(os.getenv('PRINTER_PORT', '8883'))

    if not remote_host:
        logger.error("PRINTER_HOST environment variable is required")
        sys.exit(1)

    logger.info("Starting Bambulab Printer TCP Proxy")
    logger.info(f"Configuration:")
    logger.info(f"  Bind: {local_host}:{local_port}")
    logger.info(f"  Printer: {remote_host}:{remote_port}")

    proxy = TCPProxy(local_host, local_port, remote_host, remote_port)

    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        proxy.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    proxy.start()


if __name__ == "__main__":
    main()
