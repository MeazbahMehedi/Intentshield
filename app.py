"""Run locally with python app.py; use a WSGI server for hosted use."""
from intentshield import create_app
app = create_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
