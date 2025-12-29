ARG PORT=3000
ARG PROXY_CONTENT=TRUE
ARG SOCKS5

# Only set for local/direct access. When TLS is used, the API_URL is assumed to be the same as the frontend.
ARG API_URL

# Multi-arch builder for ARM (e.g., Raspberry Pi) and x86
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

# Install system dependencies required by Reflex (e.g., curl and unzip for Bun installer)
#RUN apt-get update -y && apt-get install -y --no-install-recommends curl unzip ca-certificates \
    #&& rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip ca-certificates \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
RUN python -m venv /app/.venv && mkdir -p /app/.web
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install python app requirements and reflex in the container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install reflex helper utilities like bun/node
COPY rxconfig.py ./
RUN reflex init

# Copy local context to `/app` inside container (see .dockerignore)
COPY . .

ARG PORT API_URL PROXY_CONTENT SOCKS5
# Download other npm dependencies and compile frontend
RUN set -eux; \
  # 1) Generate .web even if the internal build fails
  REFLEX_API_URL=${API_URL:-http://localhost:$PORT} reflex export --loglevel debug --frontend-only --no-zip || true; \
  \
  # 2) Remove the static import that collides with the ClientSide const
  #    (This keeps only the dynamic import wrapper.)
  sed -i '/^import .* from "\$\/public\/player"$/d' ".web/app/routes/[watch].\$[channel_id]._index.jsx"; \
  \
  # If the collision also appears in other routes later, patch them too:
  find .web/app/routes -name '*.jsx' -print0 \
    | xargs -0 grep -l '\$\/public\/player' \
    | xargs -r sed -i '/^import .* from "\$\/public\/player"$/d'; \
  \
  # 3) Build the frontend using react-router directly
  cd .web && ./node_modules/.bin/react-router build; \
  \
  # 4) Copy build output
  mv build/client/* /srv/; \
  rm -rf /app/.web
#RUN REFLEX_API_URL=${API_URL:-http://localhost:$PORT} reflex export --loglevel debug --frontend-only --no-zip && mv .web/build/client/* /srv/ && rm -rf .web


# Final image with only necessary files
FROM --platform=$TARGETPLATFORM python:3.11-slim

# Install Caddy and redis server inside image
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    caddy redis-server && rm -rf /var/lib/apt/lists/*

ARG PORT API_URL
ENV PATH="/app/.venv/bin:$PATH" PORT=$PORT REFLEX_API_URL=${API_URL:-http://localhost:$PORT} REDIS_URL=redis://localhost PYTHONUNBUFFERED=1 PROXY_CONTENT=${PROXY_CONTENT:-TRUE} SOCKS5=${SOCKS5:-""}

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /srv /srv

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

EXPOSE $PORT

# Starting the backend.
CMD caddy start && \
    redis-server --daemonize yes && \
    exec reflex run --env prod --backend-only
