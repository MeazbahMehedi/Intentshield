"""Application settings for the local development server."""


class Config:
    """Values Flask reads when the app starts.

    SECRET_KEY is only used later for sessions and forms. The placeholder is
    fine on your own computer. Do not deploy this project with this value.
    """

    SECRET_KEY = "dev-only-not-for-deployment"
    DEBUG = True
