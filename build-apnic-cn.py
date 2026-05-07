#!/usr/bin/env python3
import ipaddress
import urllib.request
import json

apnic_url = "https://ftp.apnic.net/stats/apnic/delegated-apnic-latest"

ipv4_out: list[ipaddress.IPv4Network] = []
ipv6_out: list[ipaddress.IPv6Network] = []

with urllib.request.urlopen(apnic_url) as apnic:
    for raw in apnic:
        line = raw.decode("utf-8", errors="ignore").strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < 7:
            continue

        registry, cc, typ, start, value, date, status = parts[:7]

        if registry != "apnic":
            continue
        if cc != "CN":
            continue
        if status not in ("allocated", "assigned"):
            continue

        if typ == "ipv4":
            start_ip = ipaddress.IPv4Address(start)
            count = int(value)
            end_ip = ipaddress.IPv4Address(int(start_ip) + count - 1)

            for net in ipaddress.summarize_address_range(start_ip, end_ip):
                ipv4_out.append(net)

        elif typ == "ipv6":
            # IPv6 value 就是 prefix length
            ipv6_out.append(ipaddress.IPv6Network(f"{start}/{value}"))

geoip_apnic_cn = {
    "version": 1,
    "rules": [{"ip_cidr": [str(ip) for ip in ipv4_out + ipv6_out]}],
}

with open("rule-set/apnic-cn.json", "w") as f:
    f.write(json.dumps(geoip_apnic_cn, indent=4))

