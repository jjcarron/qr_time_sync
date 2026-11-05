FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY qr_time_sync.html /usr/share/nginx/html/qr-time-sync/index.html
