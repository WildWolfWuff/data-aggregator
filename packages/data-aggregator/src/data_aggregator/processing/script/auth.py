import httpx2

from .config import BasicAuthConfig, TokenAuthConfig


def build_request_auth(auth: BasicAuthConfig | TokenAuthConfig | None) -> tuple[httpx2.Auth | None, dict[str, str]]:
  """Return the httpx2 auth object and extra headers for the configured auth."""
  match auth:
    case BasicAuthConfig():
      return httpx2.BasicAuth(auth.username, auth.password.get_secret_value()), {}
    case TokenAuthConfig():
      token = auth.token.get_secret_value()
      return None, {auth.header: f"{auth.scheme} {token}" if auth.scheme else token}
    case None:
      return None, {}
