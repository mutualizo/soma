# Copyright (C) 2024 - MUTUALIZO ti@mutualizo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

# Este shell script foi criado com intuito de auxiliar #####
# na geração dos diagramas de forma mais prática. #####

echo "==========================="
echo "Start of script"

read -p "Diagrama é de um módulo customizado? " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
  ##### Definir nome do módulo #####
  echo "==========================="
  echo "Define Module for the diagrams to be generated"
  echo "==========================="
  read -p "Informe o módulo:" MODULE

  ##### Defini diretório para gerar os diagramas #####
  echo "==========================="
  echo "Set directory path gera"
  echo "==========================="
  DIR=custom-addons/MutualizoAddons/$MODULE/
  cd $DIR
fi
##### Verifica se o diretório "diagrams" existe, se criar #####
echo "check if directory diagrams exists if not create"
echo "==========================="
if [ -d ./diagrams/ ];
then
  echo "Diretório diagrams já existe"
else
  echo "criando diretório diagrams"
  mkdir ./diagrams/
  mkdir ./diagrams/code
  mkdir ./diagrams/img
  exit
fi

##### Gerar os diagramas de sequência #####
echo "==========================="
echo "Generate the sequence diagrams"
echo "==========================="
python3 -m plantuml ./diagrams/code/*.txt
mv ./diagrams/code/*.png ./diagrams/img/

##### Gerar os diagramas de arquitetura #####
echo "==========================="
echo "Generate the architecture diagrams"
echo "==========================="
python3 ./diagrams/code/*.py
mv ./*.png ./diagrams/img

##### Adicionar ao GIT para commit #####
echo "==========================="
echo "Add to GIT for commit"
echo "==========================="
git add ./diagrams/*

echo "End of script"
echo "==========================="

exit