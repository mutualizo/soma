FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV TERM=xterm

# Avoid ERROR: invoke-rc.d: policy-rc.d denied execution of start.
RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt update && apt upgrade -y

RUN apt install software-properties-common -y 

RUN add-apt-repository ppa:deadsnakes/ppa && apt update

# RUN apt install python3.7 -y

RUN mkdir /opt/addons && \
    mkdir /var/log/odoo && \
    mkdir /var/log/supervisord && \
    mkdir /opt/data && \
    mkdir /etc/odoo && \
    useradd --system --home /opt --shell /bin/bash --uid 1040 odoo

COPY ./conf/pip-requirements.txt /opt/sources/
COPY ./conf/apt-requirements.txt /opt/sources/

WORKDIR /opt/sources/

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get install -y --no-install-recommends $(grep -v '^#' apt-requirements.txt)

# Generate locale C.UTF-8 for postgres and general locale data
RUN locale-gen en_US en_US.UTF-8 pt_BR pt_BR.UTF-8 && dpkg-reconfigure locales
ENV LC_ALL pt_BR.UTF-8

RUN pip3 install setuptools && pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r pip-requirements.txt

# Bibliotecas da localizacao br
RUN pip3 install git+https://github.com/erpbrasil/erpbrasil.base.git
RUN pip3 install git+https://github.com/erpbrasil/erpbrasil.edoc.git
RUN pip3 install git+https://github.com/erpbrasil/erpbrasil.edoc.pdf.git
RUN pip3 install git+https://github.com/erpbrasil/erpbrasil.assinatura.git
RUN pip3 install git+https://github.com/erpbrasil/erpbrasil.transmissao.git

ADD https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb /opt/sources/wkhtmltox.deb
RUN dpkg -i wkhtmltox.deb && rm wkhtmltox.deb

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ focal"-pgdg main | tee  /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y postgresql-client-13

RUN npm install -g rtlcss

WORKDIR /opt/sources/

RUN wget https://github.com/odoo/odoo/archive/refs/heads/14.0.zip -O odoo.zip && \
    wget https://github.com/odoo/design-themes/archive/14.0.zip -O design-themes.zip && \
    wget https://github.com/OCA/account-payment/archive/14.0.zip -O account-payment.zip && \
    wget https://github.com/OCA/account-reconcile/archive/14.0.zip -O account-reconcile.zip && \
    wget https://github.com/OCA/bank-payment/archive/14.0.zip -O bank-payment.zip && \
    wget https://github.com/OCA/l10n-brazil/archive/14.0.zip -O l10n-brazil.zip && \
    wget https://github.com/muk-it/muk_web/archive/14.0.zip -O muk_web.zip && \
    wget https://github.com/OCA/bank-statement-import/archive/14.0.zip -O bank-statement-import.zip && \
    wget https://github.com/CybroOdoo/CybroAddons/archive/refs/heads/14.0.zip -O CybroAddons.zip
    

RUN unzip -q odoo.zip && rm odoo.zip && mv odoo-14.0 /opt/odoo && \
    unzip -q design-themes.zip && rm design-themes.zip && mv design-themes-14.0 /opt/addons/design-themes && \
    unzip -q account-payment.zip && rm account-payment.zip && mv account-payment-14.0 /opt/addons/account-payment && \
    unzip -q account-reconcile.zip && rm account-reconcile.zip && mv account-reconcile-14.0 /opt/addons/account-reconcile && \
    unzip -q bank-payment.zip && rm bank-payment.zip && mv bank-payment-14.0 /opt/addons/bank-payment && \
    unzip -q l10n-brazil.zip && rm l10n-brazil.zip && mv l10n-brazil-14.0 /opt/addons/l10n-brazil && \
    unzip -q muk_web.zip && rm muk_web.zip && mv muk_web-14.0 /opt/addons/muk_web && \
    unzip -q bank-statement-import.zip && rm bank-statement-import.zip && mv bank-statement-import-14.0 /opt/addons/bank-statement-import && \
    unzip -q CybroAddons.zip && rm CybroAddons.zip && mv CybroAddons-14.0 /opt/addons/CybroAddons && \
    find . -name "*.po" -not -name "pt_BR.po" -not -name "pt.po"  -type f -delete && \
    find . -path "*l10n_*" -not -name "*l10n_br*" -delete

RUN pip3 install -r /opt/addons/l10n-brazil/requirements.txt
