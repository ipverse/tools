#!/usr/bin/env python3
"""Look up the Autonomous System (AS) for an IP address using ipverse data."""

import argparse, gzip, ipaddress, json, os, sys, tarfile, time, urllib.request

TARBALL_URL = "https://github.com/ipverse/as-ip-blocks/releases/download/latest/as-ip-blocks.tar.gz"
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STALE_SECONDS = 86400


def log(msg, **kw):
    print(msg, file=sys.stderr, **kw)


def download(dest):
    log(f"Downloading {TARBALL_URL} ...")
    req = urllib.request.Request(TARBALL_URL, headers={"User-Agent": "ip2as/1.0"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while chunk := resp.read(65536):
            f.write(chunk)
            done += len(chunk)
            if total:
                log(f"\r  {done/1e6:.1f} / {total/1e6:.1f} MB ({done*100//total}%)", end="")
            else:
                log(f"\r  {done/1e6:.1f} MB", end="")
    log("")


def build_db(tarball_path):
    log("Building prefix database ...")
    entries = {"4": {}, "6": {}}
    count = 0
    with tarfile.open(tarball_path, "r:gz") as tar:
        for member in tar:
            if not member.name.endswith("/aggregated.json"):
                continue
            f = tar.extractfile(member)
            if not f:
                continue
            try:
                data = json.loads(f.read())
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            meta = data.get("metadata", {})
            info = [data.get("asn"), meta.get("handle", ""), meta.get("description", ""),
                    meta.get("countryCode", ""), meta.get("country", "")]
            for family in ("ipv4", "ipv6"):
                bucket = entries["4" if family == "ipv4" else "6"]
                for cidr in data.get("prefixes", {}).get(family, []):
                    try:
                        net = ipaddress.ip_network(cidr, strict=False)
                    except ValueError:
                        continue
                    bucket[f"{int(net.network_address)}:{net.prefixlen}"] = info
            count += 1
    log(f"  {count} autonomous systems, {len(entries['4'])} IPv4 + {len(entries['6'])} IPv6 prefixes")
    return entries


def ensure_db(data_dir, force):
    db_path = os.path.join(data_dir, "ip2as.db.gz")
    if force or not os.path.exists(db_path) or (time.time() - os.path.getmtime(db_path)) > STALE_SECONDS:
        os.makedirs(data_dir, exist_ok=True)
        tarball = os.path.join(data_dir, "as-ip-blocks.tar.gz")
        try:
            download(tarball)
            db = build_db(tarball)
            with gzip.open(db_path, "wt", encoding="utf-8") as f:
                json.dump(db, f, separators=(",", ":"))
            log(f"  Saved {db_path} ({os.path.getsize(db_path)/1e6:.1f} MB)")
        finally:
            if os.path.exists(tarball):
                os.unlink(tarball)
    with gzip.open(db_path, "rt", encoding="utf-8") as f:
        return json.load(f)


def lookup(db, query):
    try:
        net = ipaddress.ip_network(query, strict=False)
    except ValueError:
        return None
    entries = db.get(str(net.version), {})
    bits = 32 if net.version == 4 else 128
    addr = int(net.network_address)
    start = net.prefixlen if net.prefixlen < bits else bits
    for pfxlen in range(start, -1, -1):
        mask = ((1 << bits) - 1) ^ ((1 << (bits - pfxlen)) - 1)
        key = f"{addr & mask}:{pfxlen}"
        if key in entries:
            info = entries[key]
            matched = ipaddress.ip_network(((addr & mask).to_bytes(bits // 8, "big"), pfxlen))
            return {"asn": info[0], "handle": info[1], "description": info[2],
                    "countryCode": info[3], "country": info[4], "prefix": str(matched)}
    return None


def main():
    p = argparse.ArgumentParser(description="Look up AS for an IP using ipverse data.",
                                usage="%(prog)s [--force-update] [--json] [--data-dir PATH] <IP|CIDR>")
    p.add_argument("target", metavar="IP|CIDR")
    p.add_argument("--force-update", action="store_true")
    p.add_argument("--json", action="store_true", dest="json_output")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    args = p.parse_args()

    try:
        db = ensure_db(args.data_dir, args.force_update)
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

    result = lookup(db, args.target)
    if not result:
        print(json.dumps({"ip": args.target, "error": "not found"}, indent=2) if args.json_output
              else f"No AS found for {args.target}")
        sys.exit(1)

    if args.json_output:
        print(json.dumps({"ip": args.target, **result}, indent=2))
    else:
        parts = [f"AS{result['asn']}"]
        if result["handle"]: parts.append(result["handle"])
        if result["description"]: parts.append(result["description"])
        line = " - ".join(parts)
        if result["countryCode"]: line += f" ({result['countryCode']})"
        print(line)


if __name__ == "__main__":
    main()
