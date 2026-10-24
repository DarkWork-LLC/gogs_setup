import http.server
import socketserver
import os
import sys

def run_simple_server():
    try:
        PORT = 3002
        Handler = http.server.SimpleHTTPRequestHandler

        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\nSimple HTTP Server running on port {PORT}")
            print("Press Ctrl+C to stop the server")
            print("Access Gogs at: http://localhost:3000")
            print("\nNote: This is a simple server for testing purposes only.")
            print("For a production setup, you'll need to install podman or docker.")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
                return True

    except Exception as e:
        print(f"Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = run_simple_server()
    sys.exit(0 if success else 1)
