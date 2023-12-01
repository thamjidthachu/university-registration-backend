FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY university-registration-backend.conf /etc/nginx/sites-available/

RUN mkdir -p /etc/nginx/sites-enabled/\
    && ln -s /etc/nginx/sites-available/university-registration-backend.conf /etc/nginx/sites-enabled/


CMD ["nginx", "-g", "daemon off;"]