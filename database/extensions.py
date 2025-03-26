
try:
    from psycopg2cffi import compat

    # Try to use the CFFI version of psycopg2, if it's available.
    # This is necessary for usage in PyPy, which doesn't support
    # the C extension version.
    compat.register()
except ImportError:
    pass
