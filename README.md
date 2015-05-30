# updateLinodeDNS

####Table of contents

1. [Overview](#overview)
2. [Description](#description)
3. [Requirements](#requirements)
4. [Example usage](#usage)
5. [Limitations](#limitations)
6. [Todo](#todo)

##Overview

This python script was written to update a chosen DNS record in a Managed DNS zone hosted by Linode.

##Description

Linode is a popular VPS provider that provides a simple interface for Managed DNS. This python script aims to manage a
specific DNS entry, of a specific domain in order to provide a Dyanmic DNS-like solution. By making a request to
[the ipify.org](https://www.ipify.org/ "ipify.org")API generously hosted by Randall Degges, the script updates the
specified DNS record to the value provided by the API.

##Requirements

* Python 2.7 or greater
* PyCurl
* Generated API key from [https://manager.linode.com/profile/api](https://manager.linode.com/profile/api)
* A DNS zone already managed via Linode's Managed DNS
* A record that already exists

##Usage

Once you've inserted your relevant bits of data, then all that's required is to run the script periodically or trigger
as required on IP address change.

Example:

```Shell
*/30 * * * * /path/to/updateLinodeDNS.py >/dev/null 2>&1
```

I'd recommend only doing it at most, every 30 minutes, as the DNS changes will only be reflected in that timespan
anyway.

###Combining with iptables

```Shell
iptables -N SSH # Create the SSH chain
iptables -A INPUT -p tcp -m tcp --dport 22 -j SSH
iptables -A INPUT -p tcp -m tcp --dport 22 -j DROP

iptables -N DYNAMIC
iptables -A SSH -j DYNAMIC
```

And to inject your Linode hostname periodically:

```Shell
#!/bin/bash

iptables -F DYNAMIC # Flush the DYNAMIC chain
iptables -A DYNAMIC -s <hostname> -j ACCEPT
```


Credit for iptables rule suggestions: [Kamal Nasser](https://blog.kamal.io/post/ip-tables-and-dynamic-dns/)

##Limitations

* Currently, the Linode DNS servers are reloaded every half-hour ( See: [here]
(https://www.linode.com/docs/networking/dns/dns-manager "DNS Manager") )

##Todo

* Support IPv6
* Support creation of records if they do not previously exist
* Possibly support reading in files
* Possibly a tonne more error checking