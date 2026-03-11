#!/bin/bash
# Renova o certificado SSL automaticamente
# Adicione ao crontab: 0 3 * * * /opt/botcurriculo/scripts/renew-cert.sh

cd /opt/botcurriculo

docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload
