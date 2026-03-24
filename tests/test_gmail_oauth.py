from __future__ import annotations

from pathlib import Path

import gmail_oauth as module


def test_default_token_cache_path_uses_user_slug() -> None:
    path = module.default_token_cache_path("Star.Works+5@gmail.com")
    assert path.name.endswith(".json")
    assert "star-works-5-gmail-com" in path.name


def test_token_is_usable_checks_expiry() -> None:
    assert module.token_is_usable({"access_token": "abc", "expires_at": 9999999999})
    assert not module.token_is_usable({"access_token": "abc", "expires_at": 1})


def test_load_client_profile_accepts_installed_shape(tmp_path: Path) -> None:
    path = tmp_path / "client.json"
    path.write_text(
        '{"installed":{"client_id":"cid","client_secret":"secret","auth_uri":"https://auth","token_uri":"https://token","redirect_uris":["http://localhost"]}}',
        encoding="utf-8",
    )

    profile = module.load_client_profile(str(path))

    assert profile["client_id"] == "cid"
    assert profile["client_secret"] == "secret"


def test_build_xoauth2_bytes_contains_user_and_bearer() -> None:
    payload = module.build_xoauth2_bytes("user@gmail.com", "token-123")
    assert b"user=user@gmail.com" in payload
    assert b"auth=Bearer token-123" in payload
