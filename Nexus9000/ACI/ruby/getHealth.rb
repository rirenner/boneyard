#!/usr/bin/ruby

require 'acirb'

apicuri = 'https://10.95.33.232'
username = 'admin'
password = 'Cisco321'

rest = ACIrb::RestClient.new(url: apicuri, user: username,
                                 password: password)

health = rest.lookupByDn('topology/HDfabricOverallHealth5min-0',
                         subtree: 'full')
puts health.healthAvg
