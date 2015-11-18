#!/usr/bin/ruby

require 'acirb'


apicuri = 'https://10.95.33.232'
username = 'admin'
password = 'Cisco321'

rest = ACIrb::RestClient.new(url: apicuri, user: username,
                                 password: password)

uni = ACIrb::PolUni.new(nil)
tenant = ACIrb::FvTenant.new(uni, name: 'NewTenant')
tenant.create(rest)
