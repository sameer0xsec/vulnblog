FROM httpd:2.4
RUN sed -i \
    -e 's/^#LoadModule proxy_module/LoadModule proxy_module/' \
    -e 's/^#LoadModule proxy_http_module/LoadModule proxy_http_module/' \
    -e 's/^#LoadModule rewrite_module/LoadModule rewrite_module/' \
    -e 's/^#LoadModule status_module/LoadModule status_module/' \
    /usr/local/apache2/conf/httpd.conf
COPY httpd.conf /usr/local/apache2/conf/httpd.conf
