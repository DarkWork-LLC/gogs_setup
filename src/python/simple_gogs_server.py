#!/usr/bin/env python3
"""
Simple Gogs development server for when podman is not available.
This script provides a basic HTTP server for development purposes.
"""

import http.server
import socketserver
import socket
import sys

def run_simple_server():
    """Start a simple HTTP server for development"""
    try:
        # Try different ports if 3000 is busy
        for PORT in [3000, 3001, 3002, 8080, 8000]:
            try:
                Handler = http.server.SimpleHTTPRequestHandler

                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    print(f"\nSimple HTTP Server running on port {PORT}")
                    print("Press Ctrl+C to stop the server")
                    print(f"Access Gogs at: http://localhost:{PORT}")
                    print("\nNote: This is a simple server for testing purposes only.")
                    print("For a production setup with podman, install podman and try again.")
                    print("You can try: sudo apt-get install podman (Ubuntu/Debian)")
                    print("Or: sudo dnf install podman (Fedora/CentOS)")
                    print("Or: sudo yum install podman (older CentOS)")

                    try:
                        httpd.serve_forever()
                    except KeyboardInterrupt:
                        print("\nServer stopped.")
                        return True
                    except Exception as server_error:
                        print(f"Server error on port {PORT}: {server_error}")
                        continue
                        
            except socket.error as e:
                if e.errno == 98:  # Address already in use
                    print(f"Port {PORT} is busy, trying next port...")
                    continue
                else:
                    raise e
                    
        print("All common ports are busy. Cannot start server.")
        return False

    except Exception as e:
        print(f"Error starting simple server: {e}")
        return False

if __name__ == "__main__":
    print("Starting simple Gogs development server...")
    success = run_simple_server()
    sys.exit(0 if success else 1)