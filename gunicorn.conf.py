# Número de workers (procesos) que Gunicorn usará
workers = 4

# Tipo de worker (usamos uvicorn para FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"

# Dirección y puerto donde se ejecutará la aplicación
bind = "0.0.0.0:8000"

# Tiempo de espera para las solicitudes (en segundos)
timeout = 120

# Nivel de log (debug, info, warning, error, critical)
loglevel = "info"
