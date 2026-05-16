FROM nginx:alpine

# Copy index.html to a template location
COPY index.html /etc/nginx/templates/index.html.template

# Nginx alpine includes envsubst. We'll use a custom command to replace the URL.
# We replace the hardcoded http://localhost:8080 with the variable $BACKEND_URL
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/index.html.template > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"]

EXPOSE 80
