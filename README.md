# ipverse-tools

This repository contains tools that enable you to work with the ipverse data, a comprehensive database of IP addresses and associated metadata. These tools provide functionality 
for querying, analyzing, and visualizing the data to gain insights into network activity and security threats.

## Crowdsec

The `crowdsec` folder includes tools for working with Crowdsec, an open-source, lightweight software that detects and prevents peers with aggressive behaviors from 
accessing your systems. It uses a combination of behavior analysis and reputation scoring to identify and block malicious IP addresses, brute force attacks, and other types of
malicious activity.

## ip2as

The `ip2as` folder contains a Python CLI tool that does the reverse of [as-ip-blocks](https://github.com/ipverse/as-ip-blocks): given an IP address, find which AS it belongs to. Uses the as-ip-blocks data, supports IPv4/IPv6, and needs nothing beyond Python 3.
