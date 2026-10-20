from flask import Flask
import argparse


# Flask app instance
app = Flask(__name__)

# Parse command-line arguments for the Flask app
args = argparse.ArgumentParser()
args.add_argument('--port', type=int, default=8080)


@app.route('/')
def hello_world():
    return "Hello, World -- from Flask!"


if __name__ == '__main__':
    # Parse command-line arguments
    parsed_args = args.parse_args()
    port = parsed_args.port

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
