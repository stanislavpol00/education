from .base import env

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    "default": env.db(),
    # read os.environ['SQLITE_URL']
    "extra": env.db("SQLITE_URL", default="sqlite:///my-local-sqlite.db"),
}
