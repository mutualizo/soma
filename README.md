<h1 align="center">SOMA</h1>

<p align="center">
<b><a href="#Introdução">Introdução</a></b>
|
<b><a href="#Pré-requisitos">Pré-requisitos</a></b>
|
<b><a href="#Clone">Baixar o código do Soma</a></b>
|
<b><a href="#Instalação">Instalar o Soma</a></b>
|
<b><a href="#Postgresql">Criar Usuário no Postgresql</a></b>
|
<b><a href="#Executar">Executar o Soma</a></b>
|
<b><a href="#Observações">Observações</a></b>
|
<b><a href="#Licença">Licença</a></b>
<br>
</p>

# Introdução - Tutorial Instalação para Desenvolvedores

Para que funcione corretamente, é necessário estar em um sistema operacional Ubuntu 22.04.

# Pré-requisitos - Usuário do Ubuntu

* #### Criar Usuário "soma" no Ubuntu. 

Seguir o Seguinte Tutorial de Criação de Usuário: [Como criar um novo usuário no Ubuntu 22.04](https://pt.linux-console.net/?p=15024)

Observação: É necessário que o usuário seja criado com o nome "soma" (A senha está a seu critério) e seja criado como Administrador do sistema.

* #### Criar chave ssh no Github com seu usuário da Mutualizo.

# Clone - Baixar o código do Soma

* #### De permissão para o seu usuário "soma" no diretório /opt:


```sudo chmod soma:soma /opt```

* #### em seguida entre no diretório /opt e baixe o repositório do soma:


```cd /opt```

```git clone --recurse-submodules git@github.com:mutualizo/soma.git```

# Instalação - Instalar o Soma

* #### Dentro do diretório /opt/soma, execute o comando para tornar os arquivos executaveis:


```chmod 775 soma.sh diagrams.sh```  

* #### Em seguida é só instalar o Soma, com o comando a seguir:


```./soma.sh```

* #### O comando para Instalar o Soma deve ser executado sem a necessidade do "sudo" (root), caso você não consiga rodar sem o "sudo", algo está errado, revise os pré-requisitos.

# Postgresql - Criar Usuário no Postgresql

* #### Para Criar um usuário no banco de dados é necessário definir uma senha para seu usuário "postgres" (A senha está a seu critério), para isso execute:

    
```sudo su postgres```

```psql ```

```alter user postgres with password '123';```

#### Para finalizar o processo de definição de senha é necessário acessar o pgadmin com o usuário postgres e criar um usuário para o Odoo por lá

* #### Reiniciar o serviço do postgresql, para isso execute:


```sudo service postgresql restart```

* #### Abra seu DBeaver (Administrador de Banco de Dados), acesse o localhost com seu usuário postgres e a senha escolhida.

* #### Crie um usuário "soma", e com a senha "soma". É de obrigatório que tenha todos os privilégios, ou seja, na criação do usuário é preciso marcar todos os "checkbox" de permissionamento.

# Executar - Executar o Soma

* #### Para executar o soma basta executar um start no serviço, segue o comando:


```sudo service soma start```

# Observações:

* #### Consulte o log em soma/log/soma.log, segue o comando para acompanhar o log:

    
```tail -f log/soma.log```

* #### Para executar o soma de forma manual e acompanhar o log em execução, primeiro é necessário garantir que o serviço não esteja iniciado, então ganta isso com o seguinte comando:


```sudo service soma stop```

#### Em seguida dentro do diretório odoo (soma/odoo/), execute o seguinte comando:
  

```./odoo-bin --config=../init/soma.conf```

### Submódulos

* #### Sincronizar estrutura de submódulos:


```git submodules init```

* #### Para Atualizar os submódulos execute o update:


```git submodule update --remote```

* #### Para trazer submódulos novos:


```git submodule update --init --recursive```

#### É necessário fazer o commit e push das atualizações dos submódulos para manter atualizado com o repositórios externos.

# Licença

### Este projeto é de propriedade da Mutualizo.

<p align="center">
<a name="top" href="https://www.mutualizo.com.br/"><img src="https://github.com/mutualizo/soma/blob/Develop/icon.png" width="250"></a>
</p>
