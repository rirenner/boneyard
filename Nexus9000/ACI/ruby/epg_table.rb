#!/usr/bin/ruby
#
# https://github.com/datacenter/acirb
#

require 'acirb'
require 'highline/import'

host = ARGV[0].nil? ? "10.95.33.232" : ARGV[0]
apicurl = "https://#{host}"
username = "admin"
password = ask("Password:  ") { |q| q.echo = "*" }

apic = ACIrb::RestClient.new(url: apicurl, user: username, password: password)

if ARGV[1]
  cq = ACIrb::ClassQuery.new("fvAEPg")
  cq.prop_filter = 'eq(fvAEPg.name,"%s")' % [ARGV[1]]
  query_results = apic.query(cq).first
end

if query_results
  dn = query_results.dn
  dnq = ACIrb::DnQuery.new(dn)
  dnq.class_filter = "fvCEp"
  dnq.query_target = 'subtree'
  dnq.subtree = 'full'
end

system('clear')

while true
  apic.refresh_session
  if query_results
    endpoints = apic.query dnq
  else
    endpoints = apic.lookupByClass('fvCEp', subtree: 'full')
  end
  
  puts "Endpoints: #{endpoints.length}"
  endpoints.each do |endpoint|
    ip = endpoint.attributes["ip"]
    mac = endpoint.attributes["mac"]
    epg = endpoint.parent.dn
    path = endpoint.rscEpToPathEp.first.attributes["tDn"]
    encap = endpoint.attributes["encap"]
    puts "%-15s %-20s %-40s %s %s" % [ip, mac, epg, path, encap]
  end
  puts "Endpoints: #{endpoints.length}"
  sleep 5
  system('clear')
end
