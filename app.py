"""Start PromptGuard from the project folder.

Run with:
    python app.py
"""

from promptguard import create_app

app = create_app()


if __name__ == "__main__":
    # 127.0.0.1 means only this computer can open the site.
    app.run(host="127.0.0.1", port=5000, debug=True)
