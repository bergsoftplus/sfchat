FROM nginx:1.11.5

# open ssl
RUN apt-get -y install openssl

RUN mkdir /etc/nginx/ssl
RUN openssl req \
    -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/sfchat.key \
    -out /etc/nginx/ssl/sfchat.crt \
    -subj "/C=UA/ST=./L=Kyiv/O=Home/CN=sfchat.dev/OU=Development"

# configuration
RUN rm /etc/nginx/conf.d/default.conf
ADD ./nginx/config/sfchat.dev.conf /etc/nginx/conf.d/sfchat.dev.conf
