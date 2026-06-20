#!/bin/sh
set -e

# ── Persist a generated SECRET_KEY so JWT tokens survive container restarts ──
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY_FILE="/app/data/.secret_key"
    if [ -f "$SECRET_KEY_FILE" ]; then
        export SECRET_KEY="$(cat "$SECRET_KEY_FILE")"
    else
        export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
        mkdir -p /app/data
        printf '%s' "$SECRET_KEY" > "$SECRET_KEY_FILE"
        echo "[entrypoint] Generated new SECRET_KEY and saved to $SECRET_KEY_FILE"
    fi
fi

# ── Seed images: copy to uploads volume on first run ──
SEED_MARKER="/app/uploads/.seed_images_copied"
if [ ! -f "$SEED_MARKER" ] && [ -d "/app/uploads-seed" ]; then
    echo "[entrypoint] Copying seed images to uploads volume..."
    mkdir -p /app/uploads/images
    cp -r /app/uploads-seed/images/* /app/uploads/images/ 2>/dev/null || true
    touch "$SEED_MARKER"
    echo "[entrypoint] Seed images copied ($(ls /app/uploads/images/ 2>/dev/null | wc -l) files)"
fi

exec "$@"
