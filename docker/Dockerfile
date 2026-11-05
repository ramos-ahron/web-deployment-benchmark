
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-php7.2 \
    php7.2 \
    php7.2-mysql \
    php7.2-curl \
    php7.2-gd \
    php7.2-mbstring \
    php7.2-xml \
    php7.2-zip \
    php7.2-intl \
    ca-certificates \
    && a2enmod rewrite \
    && sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
