#!/usr/bin/env python2

import argparse
import boto3
import socket

p=argparse.ArgumentParser(description='Discover ip of com nameserver \
                                       for an AWS Route53 hosted zone')
p.add_argument('-d', help='AWS/Route53 domain name')
args=p.parse_args()

c=boto3.client('route53')
id=c.list_hosted_zones_by_name(DNSName=str(args.d))
comm=c.get_hosted_zone(Id=id['HostedZones'][0]['Id'].split('/')[2])['DelegationSet']['NameServers']
for c in comm:
  if 'com' in c: ip=socket.gethostbyaddr(c)
print str(ip[2]).strip('[]').strip("''")
