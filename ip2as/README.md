# ip2as

Reverse lookup: given an IP address, find the Autonomous System it belongs to. Uses [ipverse/as-ip-blocks](https://github.com/ipverse/as-ip-blocks) as the data source.

This is an example script meant as a starting point. It is not actively maintained or supported.

## How it works

On first run, the tool downloads the `as-ip-blocks` [release tarball](https://github.com/ipverse/as-ip-blocks/releases/tag/latest) (~17 MB), reads all `aggregated.json` files from it in memory, and builds a prefix lookup cache (`data/ip2as.db.gz`, ~8 MB). The tarball itself is not kept.

On subsequent runs, the cache is loaded directly. If it's older than 24 hours, it re-downloads automatically. Use `--force-update` to skip the staleness check.

Lookups work by longest-prefix-match against ~490k prefixes from ~85k autonomous systems. Both IPv4 and IPv6 are supported. You can pass a plain IP or a CIDR.

Heads up: loading the cache into Python takes about 400 MB of RAM because of all the dict entries.

## Requirements

Python 3.6+, no external dependencies.

## Usage

```
ip2as.py [--force-update] [--json] [--data-dir PATH] <IP|CIDR>
```

`--json` gives structured output. `--data-dir` changes where the cache is stored (default: `data/` next to the script).

## Examples

```
$ python3 ip2as.py 8.8.8.8
AS15169 - GOOGLE - Google LLC (US)

$ python3 ip2as.py 2001:4860::1
AS15169 - GOOGLE - Google LLC (US)

$ python3 ip2as.py --json 1.1.1.1
{
  "ip": "1.1.1.1",
  "asn": 13335,
  "handle": "CLOUDFLARENET",
  "description": "Cloudflare Inc.",
  "countryCode": "US",
  "country": "United States",
  "prefix": "1.1.1.0/24"
}

$ python3 ip2as.py 192.168.1.1
No AS found for 192.168.1.1
```
