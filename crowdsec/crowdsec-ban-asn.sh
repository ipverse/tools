#!/usr/bin/env bash
# Bans all announced networks for a given autonomous system using Crowdsec's cscli command
#
SILENT=0

while [[ "$#" -gt 0 ]]; do
  case $1 in
    -s|--silent)
      SILENT=1
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "$1" ]]; then
  echo "Usage: $0 [--silent] <ASN> <duration>"
  exit 1
fi

base_url="https://raw.githubusercontent.com/ipverse/asn-ip/master/as/$1"

ipv4_networks=$(curl -s "${base_url}/ipv4-aggregated.txt" | grep -v "^#")
ipv6_networks=$(curl -s "${base_url}/ipv6-aggregated.txt" | grep -v "^#")

if [[ -n "$ipv4_networks" && -n "$ipv6_networks" ]]; then
  networks="$ipv4_networks"$'\n'"$ipv6_networks"
elif [[ -n "$ipv4_networks" ]]; then
  networks="$ipv4_networks"
elif [[ -n "$ipv6_networks" ]]; then
  networks="$ipv6_networks"
fi

echo "$networks" | while read network; do
  if [[ $SILENT -eq 0 ]]; then
    echo "Banning network $network for $2..."
  fi
  cscli decisions add --range "$network" --duration "$2" --warning --reason "Manually banning AS$1"
done
