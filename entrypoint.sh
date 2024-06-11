#!/bin/bash

set -e

if [ -v PASSWORD_FILE ]; then
    PASSWORD="$(< $PASSWORD_FILE)"
fi


# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${PG_HOST:=${DB_PORT_5432_TCP_ADDR:=${POSTGRES_HOST:='127.0.0.1'}}}
: ${PG_PORT:=${DB_PORT_5432_TCP_PORT:=${POSTGRES_PORT:='5432'}}}
: ${PG_USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='mut_docker'}}}
: ${PG_PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

# Monta o addons_path
directories=$(ls -d -1 $PWD/addons/**)
path=","
for directory in $directories; do
  if [ -d $directory ]; then
    if [ $directory != "/opt/odoo/odoo" ]; then
      path="$path""$directory",
    fi
  fi
done
export ADDONS_PATH="$path"

# Modifica as variáveis do odoo.conf baseado em variáveis de ambiente
conf=$(cat odoo.conf | envsubst)
echo "$conf" > /etc/odoo/odoo.conf

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then       
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}

check_config "db_host" "$PG_HOST"
check_config "db_port" "$PG_PORT"
check_config "db_user" "$PG_USER"
check_config "db_password" "$PG_PASSWORD"

if [ "$UPGRADE_MODULE" ] && [ "$UPGRADE_DATABASE" ];
then
	echo "Iniciando em modo de upgrade no modulo '$UPGRADE_MODULE', na base '$UPGRADE_DATABASE'"
	sleep 5
    wait-for-psql.py ${DB_ARGS[@]} --timeout=60
	exec odoo-server "${DB_ARGS[@]}" "--update=$UPGRADE_MODULE" "--database=$UPGRADE_DATABASE"
else
	echo "Iniciando em modo normal de execução"

	case "$1" in
    	-- | odoo)
        	shift
	        if [[ "$1" == "scaffold" ]] ; then
    	        exec odoo-server "$@"
        	else
            	wait-for-psql.py ${DB_ARGS[@]} --timeout=60
	            exec odoo-server "$@" "${DB_ARGS[@]}"
    	    fi
        	;;
	    -*)
    	    wait-for-psql.py ${DB_ARGS[@]} --timeout=60
        	exec odoo-server "$@" "${DB_ARGS[@]}"
	        ;;
    	*)
        	exec "$@"
	esac
fi

exit 1
