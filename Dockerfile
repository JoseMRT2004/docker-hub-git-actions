FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY JoseMTaveras_CV.pdf /usr/share/nginx/html/
EXPOSE 80
