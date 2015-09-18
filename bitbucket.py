import os
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, redirect, url_for
from flask_dance.consumer import OAuth2ConsumerBlueprint

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["BITBUCKET_OAUTH_CLIENT_ID"] = os.environ.get("BITBUCKET_OAUTH_CLIENT_ID")
app.config["BITBUCKET_OAUTH_CLIENT_SECRET"] = os.environ.get("BITBUCKET_OAUTH_CLIENT_SECRET")
bitbucket_bp = OAuth2ConsumerBlueprint(
    "bitbucket", __name__,
    base_url="https://api.bitbucket.org/2.0",
    authorization_url="https://bitbucket.org/site/oauth2/authorize",
    token_url="https://bitbucket.org/site/oauth2/access_token",
)
bitbucket_bp.from_config["client_id"] = "BITBUCKET_OAUTH_CLIENT_ID"
bitbucket_bp.from_config["client_secret"] = "BITBUCKET_OAUTH_CLIENT_SECRET"
bitbucket = bitbucket_bp.session
app.register_blueprint(bitbucket_bp, url_prefix="/login")

@app.route("/")
def index():
    if not bitbucket.authorized:
        return redirect(url_for("bitbucket.login"))
    resp = bitbucket.get("user")
    assert resp.ok
    return "You are @{login} on BitBucket".format(login=resp.json()["login"])

if __name__ == "__main__":
    app.run()
