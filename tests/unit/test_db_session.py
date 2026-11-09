from app.core.config import Settings
from app.db.session import build_connect_args


def make(**kw: object) -> Settings:
    base = {
        "database_url": "postgresql+asyncpg://u:p@h/db",
        "database_direct_url": "postgresql+asyncpg://u:p@h/db",
        "jwt_secret": "x" * 32,
    }
    return Settings(**{**base, **kw})  # type: ignore[arg-type]


def test_tls_when_required() -> None:
    assert build_connect_args(make(database_ssl="require"))["ssl"] == "require"


def test_no_tls_for_local() -> None:
    assert "ssl" not in build_connect_args(make(database_ssl="disable"))


def test_transaction_pooler_disables_prepared_statements() -> None:
    args = build_connect_args(make(database_pooler_transaction_mode=True))
    assert args["statement_cache_size"] == 0
    assert args["prepared_statement_name_func"]() != args["prepared_statement_name_func"]()
