ARG AWS_REGION=us-east-2
FROM 652510808251.dkr.ecr.${AWS_REGION}.amazonaws.com/soma-14-base:latest

WORKDIR /opt/sources/

RUN touch /var/log/odoo/odoo-server.log && \
    touch /var/run/odoo.pid

COPY ./odoo.conf /opt/
COPY ./entrypoint.sh /
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py

RUN mkdir -p /opt/addons/MutualizoAddons

COPY ./apps/ /opt/addons/MutualizoAddons/

RUN chown -R odoo:odoo /opt/addons && \
    chown -R odoo:odoo /opt/data && \
    chown -R odoo:odoo /var/log/odoo && \
    chown -R odoo:odoo /etc/odoo && \
    chown odoo:odoo /var/run/odoo.pid

RUN ln -s /opt/odoo/odoo-bin /usr/bin/odoo-server

# Clear instalation
RUN rm -R /opt/sources/*
RUN apt-get autoremove -y && \
    apt-get autoclean

# Expose Odoo services
EXPOSE 8069 8071 8072

ENV ODOO_RC /etc/odoo/odoo.conf
ENV PG_HOST=localhost
ENV PG_PORT=5432
ENV PG_USER=odoo
ENV PG_DATABASE=False
ENV PG_PASSWORD=odoo
ENV ODOO_PASSWORD=Mutual1z02024
ENV PORT=8069
ENV LOG_FILE=False
ENV LONGPOLLING_PORT=8072
ENV WORKERS=5
ENV TIME_CPU=6000
ENV TIME_REAL=7200
ENV DB_FILTER=False
ENV LIST_DB=True
ENV DATA_DIR=/mnt/efs

WORKDIR /opt/

USER root

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
