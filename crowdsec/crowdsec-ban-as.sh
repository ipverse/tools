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

if [[ -z "$1" || -z "$2" ]]; then
  echo "Usage: $0 [--silent] <ASN> <duration>"
  exit 1
fi

asn="${1#[Aa][Ss]}"
if [[ ! "$asn" =~ ^[0-9]+$ ]]; then
  echo "Invalid ASN: $1" >&2
  exit 1
fi

base_url="https://raw.githubusercontent.com/ipverse/as-ip-blocks/refs/heads/master/as/$asn"

if ! ipv4_networks=$(curl -fsS "${base_url}/ipv4-aggregated.txt") ||
   ! ipv6_networks=$(curl -fsS "${base_url}/ipv6-aggregated.txt"); then
  echo "Failed to fetch networks for AS$asn" >&2
  exit 1
fi

networks=$(printf '%s\n%s\n' "$ipv4_networks" "$ipv6_networks" | grep -v -e "^#" -e "^$")

if [[ -z "$networks" ]]; then
  echo "No announced networks for AS$asn" >&2
  exit 1
fi

echo "$networks" | while read -r network; do
  if [[ $SILENT -eq 0 ]]; then
    echo "Banning network $network for $2..."
  fi
  cscli decisions add --range "$network" --duration "$2" --warning --reason "Manually banning AS$asn"
done
