#!/bin/sh

# Check the environment variables
for var_name in SHARED_KEY AGENTS_API_KEY MODEL_API_KEY MODEL_API_URL AGENTS_API_URL
do
    if [ -z "`eval echo \\\$$var_name`" ]; then
        echo "Error: Environment variable '$var_name' is not set."
        exit 1
    fi
done

envsubst < /etc/traefik/traefik.yml.template > /etc/traefik/traefik.yml
exec traefik
