"""Dev entrypoint:  python run.py   (http://localhost:5000)
For production use a WSGI server, e.g.:  gunicorn 'app:create_app()' -b 0.0.0.0:5000
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
