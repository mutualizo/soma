sudo apt update

sudo apt-get upgrade -y

sudo apt install postgresql postgresql-contrib -y

sudo apt-get install git python3 python3-pip build-essential wget python3-dev python3-venv python3-wheel libxslt-dev libzip-dev libldap2-dev libsasl2-dev python3-setuptools node-less libjpeg-dev gdebi -y

sudo apt-get install libpq-dev python3-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev python3-psutil python3-polib python3-dateutil python3-decorator python3-lxml python3-reportlab python3-pil python3-passlib python3-werkzeug python3-psycopg2 python3-pypdf2 python3-gevent -y

sudo apt-get install nodejs npm -y

sudo apt-get install xfonts-75dpi xfonts-base -y

sudo apt-get install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl -y

wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb

sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb

rm -rfv /opt/soma/wkhtmltox*

pip3 install wheel

pip3 install -r /opt/soma/odoo/requirements.txt

sudo snap install dbeaver-ce

sudo cp /opt/soma/init/soma /etc/init.d/

sudo chmod +x /etc/init.d/soma

sudo update-rc.d soma defaults

if [ ! -d /opt/soma/log ];
then
    mkdir /opt/soma/log
fi

sudo service soma start
