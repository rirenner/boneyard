#!/usr/bin/ruby

require 'acirb'
require 'optparse'
require 'highline/import'

options = {}

optparse = OptionParser.new do|opts|
    # set a banner
    # for help
    opts.banner = "Usage: getHealth.rb"

    options[:ip] = nil
    opts.on( '-i', '--ip IP', 'IP address to connect to') do|ipv|
        options[:ip] = ipv
    end

    options[:username] = nil
    opts.on( '-u', '--user USER', 'Username') do|user|
        options[:username] = user 
    end

    options[:password] = nil
    opts.on( '-p', '--pass PASSWORD', 'Password') do|pass|
        options[:password] = pass 
    end

    options[:tenant] = nil
    opts.on( '-t', '--tenant TENANT', 'Tenant') do|tenant|
        options[:tenant] = tenant 
    end

    opts.on( '-h', '--help', 'Display help' ) do
        puts opts
        exit
    end
end

optparse.parse!

if options[:ip] == nil 
  options[:ip] = ask("IP Address:  ")
end

if options[:username] == nil 
  options[:username] = ask("Username:  ")
end

if options[:password] == nil 
  options[:password] = ask("Password:  ") { |q| q.echo = "*" }
end

if options[:tenant] == nil 
  options[:tenant] = ask("Tenant:  ")
end

#puts "ip is #{options[:ip]}" if options[:ip]
#puts "user is #{options[:username]}" if options[:username]
#puts "password is #{options[:password]}" if options[:password]
     
apicuri = "https://#{options[:ip]}"
username = options[:username] 
password = options[:password]
tenant = options[:tenant]


rest = ACIrb::RestClient.new(url: apicuri, user: username,
                                 password: password)

uni = ACIrb::PolUni.new(nil)
tenant = ACIrb::FvTenant.new(uni, name: tenant)
tenant.create(rest)
