import os

ENVIRONMENT = os.getenv('LaCosaEnv', 'test')

DATABASE_FILENAME = f"database_{ENVIRONMENT}.sqlite"
