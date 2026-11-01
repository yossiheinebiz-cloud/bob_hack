# Same content as the GitHub Pages build: design/v2, sample receipts, the v2 spec, plus the dashboard.
FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY design/v2 /usr/share/nginx/html/design/v2
COPY data/startup/receipts /usr/share/nginx/html/data/startup/receipts
COPY data/startup/README.md /usr/share/nginx/html/data/startup/README.md
COPY dashboard /usr/share/nginx/html/dashboard
COPY 08-spec-v2.md /usr/share/nginx/html/08-spec-v2.md
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1/health || exit 1
