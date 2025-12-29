import importlib

import pytest

import rxconfig


@pytest.fixture
def reload_config(monkeypatch):
    def _reload(**env):
        for key, value in env.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
        return importlib.reload(rxconfig).config

    yield _reload
    with monkeypatch.context() as cleanup:
        cleanup.delenv("API_URL", raising=False)
        cleanup.delenv("FLARESOLVERR_URL", raising=False)
        cleanup.delenv("FLARESOLVERR_TIMEOUT", raising=False)
        cleanup.delenv("PORT", raising=False)
        importlib.reload(rxconfig)


def test_api_url_defaults_to_localhost_port(reload_config, monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    config = reload_config(PORT="4321")
    assert config.api_url == "http://localhost:4321"


def test_invalid_api_url_is_rejected(reload_config):
    with pytest.raises(ValueError):
        reload_config(API_URL="example.com")


def test_invalid_flaresolverr_url_is_rejected(reload_config):
    with pytest.raises(ValueError):
        reload_config(FLARESOLVERR_URL="ftp://example.com")
