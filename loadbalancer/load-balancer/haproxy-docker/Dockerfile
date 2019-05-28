FROM haproxy:1.8
ENV HAPROXY_USER haproxy


RUN apt update

#halog install
RUN apt install -y gcc wget make &&\
    cd /usr/src && \
    wget http://haproxy.1wt.eu/download/1.5/src/devel/haproxy-1.5-dev11.tar.gz && \
    tar xzf haproxy-1.5-dev11.tar.gz && \
    cd haproxy-1.5-dev11/contrib/halog && \
    make && \
    cp halog /usr/bin/

#haproxy
RUN apt install -y rsyslog
RUN sed -i '/module(load="imudp")/s/^#//g' /etc/rsyslog.conf && \
    sed -i '/input(type="imudp" port="514")/s/^#//g' /etc/rsyslog.conf

COPY haproxy.conf /etc/rsyslog.d/

RUN groupadd --system ${HAPROXY_USER} && \
    useradd --system --gid ${HAPROXY_USER} ${HAPROXY_USER} && \
    mkdir --parents /var/lib/${HAPROXY_USER} && \
    chown -R ${HAPROXY_USER}:${HAPROXY_USER} /var/lib/${HAPROXY_USER} && \
    mkdir --parents /run/${HAPROXY_USER}

COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
