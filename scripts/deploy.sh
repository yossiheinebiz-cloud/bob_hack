#!/usr/bin/env bash
# Production deploy on the droplet: pull main, rebuild the image (serves design/v2 and the dashboard),
# swap the container, verify. A failed build keeps the old container running.
set -euo pipefail
cd "$(dirname "$0")/.."
exec 9>/tmp/eifo-money-deploy.lock; flock 9
git fetch -q origin main
git merge -q --ff-only origin/main
docker compose build --pull
docker compose up -d --remove-orphans
for i in $(seq 1 20); do
  if curl -fsS -o /dev/null http://127.0.0.1:3050/health && curl -fsS -o /dev/null http://127.0.0.1:3050/; then
    docker image prune -f >/dev/null
    echo "deployed $(git log --oneline -1)"; exit 0
  fi
  sleep 1
done
echo "health check failed" >&2; docker compose logs --tail 30 site >&2; exit 1
