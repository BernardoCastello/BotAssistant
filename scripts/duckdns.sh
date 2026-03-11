#!/bin/bash
# Script para atualizar o IP no DuckDNS automaticamente
# Adicione ao crontab: */5 * * * * /opt/botcurriculo/scripts/duckdns.sh

DOMAIN="SEU_SUBDOMINIO"       # sem .duckdns.org
TOKEN="SEU_TOKEN_DUCKDNS"     # token do painel duckdns.org

echo url="https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=" \
  | curl -k -o /tmp/duckdns.log -K -
