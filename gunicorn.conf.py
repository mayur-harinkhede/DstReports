import multiprocessing

# Gunicorn configuration file for Render deployment
# Extend timeout to 180s to easily accommodate heavy multi-route PDF generations
timeout = 180

# Keep 2 workers for concurrency on free/starter instances
workers = 2

# Limit max requests per worker before recycling to prevent any potential memory leak
max_requests = 100
max_requests_jitter = 20

# Bind to 0.0.0.0
bind = "0.0.0.0:10000"
