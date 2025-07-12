import http.server
import socketserver
import sys
import os

PORT = 8000 # Default port

class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from the current directory."""
    def __init__(self, *args, **kwargs):
        # Set the directory to serve from to the script's directory
        # This might need adjustment if the user runs the script from elsewhere
        # but for a self-contained tool, this is a reasonable default.
        # Alternatively, could serve from the current working directory.
        # Let's stick to the current working directory for flexibility.
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    # Add basic POST handling for future upload feature (placeholder)
    # def do_POST(self):
    #     # This is a placeholder for future upload functionality
    #     self.send_response(200)
    #     self.end_headers()
    #     self.wfile.write(b"Upload functionality not yet implemented.")


if __name__ == "__main__":
    # Check for port argument
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid port number '{sys.argv[1]}'. Using default port {PORT}.")

    try:
        # Use ThreadingTCPServer to handle multiple requests concurrently
        # For a simple local tool, TCPServer might be sufficient, but threading is safer.
        with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
            print(f"Serving files from directory: {os.getcwd()}")
            print(f"Server started on port {PORT}")
            print(f"Access files at http://<your_local_ip>:{PORT}")
            print("Press Ctrl+C to stop the server.")
            httpd.serve_forever()
    except OSError as e:
        print(f"Error: Could not start server on port {PORT}. {e}")
        print("Port may already be in use.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
