#!/usr/bin/env python
#
# Linode DNS hostname update script
# Copyright (C) 2015  Leif Terrens
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Usage:
#
# api_key       - Your api key from https://manager.linode.com/profile/api
# domain        - The domain which exists in DNS Manager that the record exists in
# record        - The record you wish to update
# query_interface    - The preferred interface to send the query via ( default: eth0 )
#
#

apikey = ''
domain = ''
record = ''
query_interface = ''

ipapi = 'https://api.ipify.org'
linodeapi = 'https://api.linode.com'

import pycurl
import json
import socket

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

def query(c, url):
    buffer = BytesIO()
    c.setopt(c.INTERFACE, query_interface)
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.reset()
    return buffer

def main():
    curl = pycurl.Curl()

    # Find our current IP address
    # See: https://www.ipify.org
    # Thanks to Randall Degges for providing this service.
    try:
        ip = query(curl, ipapi).getvalue().decode('utf-8')
        socket.inet_aton(ip)
    except pycurl.error as e:
        print("FAIL %s") % e[1]
        return e[0]
    except socket.error as e:
        print("FAIL Error in obtaining source IP")
        return 99

    # Get the Domain ID via the Linode API
    # See: https://www.linode.com/api/dns/domain.list
    try:
        domain_id_query = linodeapi + "?api_key=" + apikey + "&api_action=domain.list"
        domain_data = json.loads(query(curl, domain_id_query).getvalue().decode('utf-8'))
        for api_domain in (domain_data['DATA']):
            if api_domain['DOMAIN'] == domain:
                domain_id = api_domain['DOMAINID']
                if not isinstance(domain_id, int):
                    raise TypeError("The Domain ID is not an integer")
    except pycurl.error as e:
        print("FAIL %s") % e[1]
        return e[0]
    except TypeError as e:
        print("FAIL Error in obtaining Domain ID")
        return 99

    # Get the Resource ID via the Linode API
    # See: https://www.linode.com/api/dns/domain.resource.list
    try:
        resource_id_query = linodeapi + "?api_key=" + apikey + "&api_action=domain.resource.list&DomainID=" + str(domain_id)
        resource_data = json.loads(query(curl, resource_id_query).getvalue().decode('utf-8'))
        for resource in (resource_data['DATA']):
            if resource['NAME'] == record:
                resource_id = resource['RESOURCEID']
                resource_ttl = resource['TTL_SEC']
                resource_type = resource['TYPE']
                if not isinstance(resource_id, int):
                    raise TypeError("The Resource ID is not an integer")
    except pycurl.error as e:
        print("FAIL %s") % e[1]
        return e[0]
    except TypeError as e:
        print("FAIL Error in obtaining resource ID")
        return 99

    print("Updating %s.%s to %s") % (record,domain,ip)

    # Set the Resource target via the Linode API
    # See: https://www.linode.com/api/dns/domain.resource.update
    try:
        update_query = linodeapi + "?api_key=" + apikey + "&api_action=domain.resource.update&DomainID=" + str(domain_id) + "&ResourceID=" + str(resource_id) + "&Target=" + ip
        update_response = json.loads(query(curl, update_query).getvalue().decode('utf-8'))
        if not update_response['ERRORARRAY']:
            print("OK %s.%s.\t%s\t%s\t%s") % (record, domain,resource_ttl,resource_type.upper(),ip)
            return 0
    except pycurl.error as e:
        print("FAIL %s") % e[1]
        return e[0]

if __name__ == '__main__':
     exit(main())