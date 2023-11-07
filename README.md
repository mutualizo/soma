# Soma

Fazer o clone no diretório /opt

Adicionar usuário aos sudoers

usermod -aG sudo

Rodar Instalação (não rodar o script como root (sudo)):
./opt/soma/soma.sh

Caso não seja possível a execução de permissão para o arquivo:
chmod 777 /opt/soma/soma.sh

Depois mudar o grupo e o usuário propretário

sudo service odoo status

Em /opt/soma/odoo:
./odoo-bin --config=/opt/soma/init/odoo.conf

sudo su postgres
psql
alter user postgres with password '123';
criar o Usuário odoo no banco pelo administrador (dbeaver)
