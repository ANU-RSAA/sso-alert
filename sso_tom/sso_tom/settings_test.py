from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'ATOMIC_REQUESTS': True,
        "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
    },
}

TEST_OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'test_output')
