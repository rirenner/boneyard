::cisco::eem::event_register_timer watchdog name stattimer sec $_stat_timer maxrun 600


#------------------------------------------------------------------
# EEM policy which triggers periodically and sends
# statistics info to the specified URL.
#
# November 2011, Jason Pfeifer 
#
# Copyright (c) 2011 by cisco Systems, Inc.
# All rights reserved.
#------------------------------------------------------------------

### The following EEM environment variables are used:
###
### _stat_timer (mandatory)    - The time in seconds in which you want the  
###                             policy to trigger and collect stats.
### Example: _stat_timer        30 
###
### _statcoll_url (mandatory) - The URL location to which the
###                             statistics are sent.
### Example: _statcoll_url      http://customerurlloc.com/statcollector.cgi
###
### _stat_changes (optional)  - Display Incremental statistics change 
###                             information.
### Example: _stat_changes      1
###
### _stat_debug (optional)    - Display policy debugging information.
### Example: _stat_debug        1
###

namespace import ::cisco::eem::*
namespace import ::cisco::lib::*

#############################


# http.tcl --
#
#	Client-side HTTP for GET, POST, and HEAD commands.
#	These routines can be used in untrusted code that uses 
#	the Safesock security policy.  These procedures use a 
#	callback interface to avoid using vwait, which is not 
#	defined in the safe base.
#
# See the file "license.terms" for information on usage and
# redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
#
# RCS: @(#) $Id: http.tcl,v 1.42 2002/08/20 15:33:32 dgp Exp $

# Rough version history:
# 1.0	Old http_get interface
# 2.0	http:: namespace and http::geturl
# 2.1	Added callbacks to handle arriving data, and timeouts
# 2.2	Added ability to fetch into a channel
# 2.3	Added SSL support, and ability to post from a channel
#	This version also cleans up error cases and eliminates the
#	"ioerror" status in favor of raising an error
# 2.4	Added -binary option to http::geturl and charset element
#	to the state array.

package require Tcl 8.2
# keep this in sync with pkgIndex.tcl
# and with the install directories in Makefiles
package provide http 2.4.2

namespace eval http {
    variable http
    array set http {
	-accept */*
	-proxyhost {}
	-proxyport {}
	-proxyfilter http::ProxyRequired
    }
    set http(-useragent) "Tcl http client package [package provide http]"

    proc init {} {
	variable formMap
	variable alphanumeric a-zA-Z0-9
	for {set i 0} {$i <= 256} {incr i} {
	    set c [format %c $i]
	    if {![string match \[$alphanumeric\] $c]} {
		set formMap($c) %[format %.2x $i]
	    }
	}
	# These are handled specially
	array set formMap { " " + \n %0d%0a }
    }
    init

    variable urlTypes
    array set urlTypes {
	http	{80 ::socket}
    }

    variable encodings [string tolower [encoding names]]
    # This can be changed, but iso8859-1 is the RFC standard.
    variable defaultCharset "iso8859-1"

    namespace export geturl config reset wait formatQuery register unregister
    # Useful, but not exported: data size status code
}

# http::register --
#
#     See documentaion for details.
#
# Arguments:
#     proto           URL protocol prefix, e.g. https
#     port            Default port for protocol
#     command         Command to use to create socket
# Results:
#     list of port and command that was registered.

proc http::register {proto port command} {
    variable urlTypes
    set urlTypes($proto) [list $port $command]
}

# http::unregister --
#
#     Unregisters URL protocol handler
#
# Arguments:
#     proto           URL protocol prefix, e.g. https
# Results:
#     list of port and command that was unregistered.

proc http::unregister {proto} {
    variable urlTypes
    if {![info exists urlTypes($proto)]} {
	return -code error "unsupported url type \"$proto\""
    }
    set old $urlTypes($proto)
    unset urlTypes($proto)
    return $old
}

# http::config --
#
#	See documentaion for details.
#
# Arguments:
#	args		Options parsed by the procedure.
# Results:
#        TODO

proc http::config {args} {
    variable http
    set options [lsort [array names http -*]]
    set usage [join $options ", "]
    if {[llength $args] == 0} {
	set result {}
	foreach name $options {
	    lappend result $name $http($name)
	}
	return $result
    }
    regsub -all -- - $options {} options
    set pat ^-([join $options |])$
    if {[llength $args] == 1} {
	set flag [lindex $args 0]
	if {[regexp -- $pat $flag]} {
	    return $http($flag)
	} else {
	    return -code error "Unknown option $flag, must be: $usage"
	}
    } else {
	foreach {flag value} $args {
	    if {[regexp -- $pat $flag]} {
		set http($flag) $value
	    } else {
		return -code error "Unknown option $flag, must be: $usage"
	    }
	}
    }
}

# http::Finish --
#
#	Clean up the socket and eval close time callbacks
#
# Arguments:
#	token	    Connection token.
#	errormsg    (optional) If set, forces status to error.
#       skipCB      (optional) If set, don't call the -command callback.  This
#                   is useful when geturl wants to throw an exception instead
#                   of calling the callback.  That way, the same error isn't
#                   reported to two places.
#
# Side Effects:
#        Closes the socket

proc http::Finish { token {errormsg ""} {skipCB 0}} {
    variable $token
    upvar 0 $token state
    global errorInfo errorCode
    if {[string length $errormsg] != 0} {
	set state(error) [list $errormsg $errorInfo $errorCode]
	set state(status) error
    }
    catch {close $state(sock)}
    catch {after cancel $state(after)}
    if {[info exists state(-command)] && !$skipCB} {
	if {[catch {eval $state(-command) {$token}} err]} {
	    if {[string length $errormsg] == 0} {
		set state(error) [list $err $errorInfo $errorCode]
		set state(status) error
	    }
	}
	if {[info exist state(-command)]} {
	    # Command callback may already have unset our state
	    unset state(-command)
	}
    }
}

# http::reset --
#
#	See documentaion for details.
#
# Arguments:
#	token	Connection token.
#	why	Status info.
#
# Side Effects:
#       See Finish

proc http::reset { token {why reset} } {
    variable $token
    upvar 0 $token state
    set state(status) $why
    catch {fileevent $state(sock) readable {}}
    catch {fileevent $state(sock) writable {}}
    Finish $token
    if {[info exists state(error)]} {
	set errorlist $state(error)
	unset state
	eval ::error $errorlist
    }
}

# http::geturl --
#
#	Establishes a connection to a remote url via http.
#
# Arguments:
#       url		The http URL to goget.
#       args		Option value pairs. Valid options include:
#				-blocksize, -validate, -headers, -timeout
# Results:
#	Returns a token for this connection.
#	This token is the name of an array that the caller should
#	unset to garbage collect the state.

proc http::geturl { url args } {
    variable http
    variable urlTypes
    variable defaultCharset

    # Initialize the state variable, an array.  We'll return the
    # name of this array as the token for the transaction.

    if {![info exists http(uid)]} {
	set http(uid) 0
    }
    set token [namespace current]::[incr http(uid)]
    variable $token
    upvar 0 $token state
    reset $token

    # Process command options.

    array set state {
	-binary		false
	-blocksize 	8192
	-queryblocksize 8192
	-validate 	0
	-headers 	{}
	-timeout 	0
	-type           application/x-www-form-urlencoded
	-queryprogress	{}
	state		header
	meta		{}
	coding		{}
	currentsize	0
	totalsize	0
	querylength	0
	queryoffset	0
        type            text/html
        body            {}
	status		""
	http            ""
    }
    set state(charset)	$defaultCharset
    set options {-binary -blocksize -channel -command -handler -headers \
	    -progress -query -queryblocksize -querychannel -queryprogress\
	    -validate -timeout -type}
    set usage [join $options ", "]
    regsub -all -- - $options {} options
    set pat ^-([join $options |])$
    foreach {flag value} $args {
	if {[regexp $pat $flag]} {
	    # Validate numbers
	    if {[info exists state($flag)] && \
		    [string is integer -strict $state($flag)] && \
		    ![string is integer -strict $value]} {
		unset $token
		return -code error "Bad value for $flag ($value), must be integer"
	    }
	    set state($flag) $value
	} else {
	    unset $token
	    return -code error "Unknown option $flag, can be: $usage"
	}
    }

    # Make sure -query and -querychannel aren't both specified

    set isQueryChannel [info exists state(-querychannel)]
    set isQuery [info exists state(-query)]
    if {$isQuery && $isQueryChannel} {
	unset $token
	return -code error "Can't combine -query and -querychannel options!"
    }

    # Validate URL, determine the server host and port, and check proxy case

    if {![regexp -nocase {^(([^:]*)://)?([^/:]+)(:([0-9]+))?(/.*)?$} $url \
	    x prefix proto host y port srvurl]} {
	unset $token
	return -code error "Unsupported URL: $url"
    }
    if {[string length $proto] == 0} {
	set proto http
	set url ${proto}://$url
    }
    if {![info exists urlTypes($proto)]} {
	unset $token
	return -code error "Unsupported URL type \"$proto\""
    }
    set defport [lindex $urlTypes($proto) 0]
    set defcmd [lindex $urlTypes($proto) 1]

    if {[string length $port] == 0} {
	set port $defport
    }
    if {[string length $srvurl] == 0} {
	set srvurl /
    }
    if {[string length $proto] == 0} {
	set url http://$url
    }
    set state(url) $url
    if {![catch {$http(-proxyfilter) $host} proxy]} {
	set phost [lindex $proxy 0]
	set pport [lindex $proxy 1]
    }

    # If a timeout is specified we set up the after event
    # and arrange for an asynchronous socket connection.

    if {$state(-timeout) > 0} {
	set state(after) [after $state(-timeout) \
		[list http::reset $token timeout]]
	set async -async
    } else {
	set async ""
    }

    # If we are using the proxy, we must pass in the full URL that
    # includes the server name.

    if {[info exists phost] && [string length $phost]} {
	set srvurl $url
	set conStat [catch {eval $defcmd $async {$phost $pport}} s]
    } else {
	set conStat [catch {eval $defcmd $async {$host $port}} s]
    }
    if {$conStat} {

	# something went wrong while trying to establish the connection
	# Clean up after events and such, but DON'T call the command callback
	# (if available) because we're going to throw an exception from here
	# instead.
	Finish $token "" 1
	cleanup $token
	return -code error $s
    }
    set state(sock) $s

    # Wait for the connection to complete

    if {$state(-timeout) > 0} {
	fileevent $s writable [list http::Connect $token]
	http::wait $token

	if {[string equal $state(status) "error"]} {
	    # something went wrong while trying to establish the connection
	    # Clean up after events and such, but DON'T call the command
	    # callback (if available) because we're going to throw an 
	    # exception from here instead.
	    set err [lindex $state(error) 0]
	    cleanup $token
	    return -code error $err
	} elseif {![string equal $state(status) "connect"]} {
	    # Likely to be connection timeout
	    return $token
	}
	set state(status) ""
    }

    # Send data in cr-lf format, but accept any line terminators

    fconfigure $s -translation {auto crlf} -buffersize $state(-blocksize)

    # The following is disallowed in safe interpreters, but the socket
    # is already in non-blocking mode in that case.

    catch {fconfigure $s -blocking off}
    set how GET
    if {$isQuery} {
	set state(querylength) [string length $state(-query)]
	if {$state(querylength) > 0} {
	    set how POST
	    set contDone 0
	} else {
	    # there's no query data
	    unset state(-query)
	    set isQuery 0
	}
    } elseif {$state(-validate)} {
	set how HEAD
    } elseif {$isQueryChannel} {
	set how POST
	# The query channel must be blocking for the async Write to
	# work properly.
	fconfigure $state(-querychannel) -blocking 1 -translation binary
	set contDone 0
    }

    if {[catch {
	puts $s "$how $srvurl HTTP/1.0"
	puts $s "Accept: $http(-accept)"
	if {$port == $defport} {
	    # Don't add port in this case, to handle broken servers.
	    # [Bug #504508]
	    puts $s "Host: $host"
	} else {
	    puts $s "Host: $host:$port"
	}
	puts $s "User-Agent: $http(-useragent)"
	foreach {key value} $state(-headers) {
	    regsub -all \[\n\r\]  $value {} value
	    set key [string trim $key]
	    if {[string equal $key "Content-Length"]} {
		set contDone 1
		set state(querylength) $value
	    }
	    if {[string length $key]} {
		puts $s "$key: $value"
	    }
	}
	if {$isQueryChannel && $state(querylength) == 0} {
	    # Try to determine size of data in channel
	    # If we cannot seek, the surrounding catch will trap us

	    set start [tell $state(-querychannel)]
	    seek $state(-querychannel) 0 end
	    set state(querylength) \
		    [expr {[tell $state(-querychannel)] - $start}]
	    seek $state(-querychannel) $start
	}

	# Flush the request header and set up the fileevent that will
	# either push the POST data or read the response.
	#
	# fileevent note:
	#
	# It is possible to have both the read and write fileevents active
	# at this point.  The only scenario it seems to affect is a server
	# that closes the connection without reading the POST data.
	# (e.g., early versions TclHttpd in various error cases).
	# Depending on the platform, the client may or may not be able to
	# get the response from the server because of the error it will
	# get trying to write the post data.  Having both fileevents active
	# changes the timing and the behavior, but no two platforms
	# (among Solaris, Linux, and NT)  behave the same, and none 
	# behave all that well in any case.  Servers should always read thier
	# POST data if they expect the client to read their response.
		
	if {$isQuery || $isQueryChannel} {
	    puts $s "Content-Type: $state(-type)"
	    if {!$contDone} {
		puts $s "Content-Length: $state(querylength)"
	    }
	    puts $s ""
	    fconfigure $s -translation {auto binary}
	    fileevent $s writable [list http::Write $token]
	} else {
	    puts $s ""
	    flush $s
	    fileevent $s readable [list http::Event $token]
	}

	if {! [info exists state(-command)]} {

	    # geturl does EVERYTHING asynchronously, so if the user
	    # calls it synchronously, we just do a wait here.

	    wait $token
	    if {[string equal $state(status) "error"]} {
		# Something went wrong, so throw the exception, and the
		# enclosing catch will do cleanup.
		return -code error [lindex $state(error) 0]
	    }		
	}
    } err]} {
	# The socket probably was never connected,
	# or the connection dropped later.

	# Clean up after events and such, but DON'T call the command callback
	# (if available) because we're going to throw an exception from here
	# instead.
	
	# if state(status) is error, it means someone's already called Finish
	# to do the above-described clean up.
	if {[string equal $state(status) "error"]} {
	    Finish $token $err 1
	}
	cleanup $token
	return -code error $err
    }

    return $token
}

# Data access functions:
# Data - the URL data
# Status - the transaction status: ok, reset, eof, timeout
# Code - the HTTP transaction code, e.g., 200
# Size - the size of the URL data

proc http::data {token} {
    variable $token
    upvar 0 $token state
    return $state(body)
}
proc http::status {token} {
    variable $token
    upvar 0 $token state
    return $state(status)
}
proc http::code {token} {
    variable $token
    upvar 0 $token state
    return $state(http)
}
proc http::ncode {token} {
    variable $token
    upvar 0 $token state
    if {[regexp {[0-9]{3}} $state(http) numeric_code]} {
	return $numeric_code
    } else {
	return $state(http)
    }
}
proc http::size {token} {
    variable $token
    upvar 0 $token state
    return $state(currentsize)
}

proc http::error {token} {
    variable $token
    upvar 0 $token state
    if {[info exists state(error)]} {
	return $state(error)
    }
    return ""
}

# http::cleanup
#
#	Garbage collect the state associated with a transaction
#
# Arguments
#	token	The token returned from http::geturl
#
# Side Effects
#	unsets the state array

proc http::cleanup {token} {
    variable $token
    upvar 0 $token state
    if {[info exist state]} {
	unset state
    }
}

# http::Connect
#
#	This callback is made when an asyncronous connection completes.
#
# Arguments
#	token	The token returned from http::geturl
#
# Side Effects
#	Sets the status of the connection, which unblocks
# 	the waiting geturl call

proc http::Connect {token} {
    variable $token
    upvar 0 $token state
    global errorInfo errorCode
    if {[eof $state(sock)] ||
	[string length [fconfigure $state(sock) -error]]} {
	    Finish $token "connect failed [fconfigure $state(sock) -error]" 1
    } else {
	set state(status) connect
	fileevent $state(sock) writable {}
    }
    return
}

# http::Write
#
#	Write POST query data to the socket
#
# Arguments
#	token	The token for the connection
#
# Side Effects
#	Write the socket and handle callbacks.

proc http::Write {token} {
    variable $token
    upvar 0 $token state
    set s $state(sock)
    
    # Output a block.  Tcl will buffer this if the socket blocks
    
    set done 0
    if {[catch {
	
	# Catch I/O errors on dead sockets

	if {[info exists state(-query)]} {
	    
	    # Chop up large query strings so queryprogress callback
	    # can give smooth feedback

	    puts -nonewline $s \
		    [string range $state(-query) $state(queryoffset) \
		    [expr {$state(queryoffset) + $state(-queryblocksize) - 1}]]
	    incr state(queryoffset) $state(-queryblocksize)
	    if {$state(queryoffset) >= $state(querylength)} {
		set state(queryoffset) $state(querylength)
		set done 1
	    }
            flush $s
            after 5
	} else {
	    
	    # Copy blocks from the query channel

	    set outStr [read $state(-querychannel) $state(-queryblocksize)]
	    puts -nonewline $s $outStr
	    incr state(queryoffset) [string length $outStr]
	    if {[eof $state(-querychannel)]} {
		set done 1
	    }
	}
    } err]} {
	# Do not call Finish here, but instead let the read half of
	# the socket process whatever server reply there is to get.

	set state(posterror) $err
	set done 1
    }
    if {$done} {
	catch {flush $s}
	fileevent $s writable {}
	fileevent $s readable [list http::Event $token]
    }

    # Callback to the client after we've completely handled everything

    if {[string length $state(-queryprogress)]} {
	eval $state(-queryprogress) [list $token $state(querylength)\
		$state(queryoffset)]
    }
}

# http::Event
#
#	Handle input on the socket
#
# Arguments
#	token	The token returned from http::geturl
#
# Side Effects
#	Read the socket and handle callbacks.

proc http::Event {token} {
    variable $token
    upvar 0 $token state
    set s $state(sock)

     if {[eof $s]} {
	Eof $token
	return
    }
    if {[string equal $state(state) "header"]} {
	if {[catch {gets $s line} n]} {
	    Finish $token $n
	} elseif {$n == 0} {
	    variable encodings
	    set state(state) body
	    if {$state(-binary) || ![regexp -nocase ^text $state(type)] || \
		    [regexp gzip|compress $state(coding)]} {
		# Turn off conversions for non-text data
		fconfigure $s -translation binary
		if {[info exists state(-channel)]} {
		    fconfigure $state(-channel) -translation binary
		}
	    } else {
		# If we are getting text, set the incoming channel's
		# encoding correctly.  iso8859-1 is the RFC default, but
		# this could be any IANA charset.  However, we only know
		# how to convert what we have encodings for.
		set idx [lsearch -exact $encodings \
			[string tolower $state(charset)]]
		if {$idx >= 0} {
		    fconfigure $s -encoding [lindex $encodings $idx]
		}
	    }
	    if {[info exists state(-channel)] && \
		    ![info exists state(-handler)]} {
		# Initiate a sequence of background fcopies
		fileevent $s readable {}
		CopyStart $s $token
	    }
	} elseif {$n > 0} {
	    if {[regexp -nocase {^content-type:(.+)$} $line x type]} {
		set state(type) [string trim $type]
		# grab the optional charset information
		regexp -nocase {charset\s*=\s*(\S+)} $type x state(charset)
	    }
	    if {[regexp -nocase {^content-length:(.+)$} $line x length]} {
		set state(totalsize) [string trim $length]
	    }
	    if {[regexp -nocase {^content-encoding:(.+)$} $line x coding]} {
		set state(coding) [string trim $coding]
	    }
	    if {[regexp -nocase {^([^:]+):(.+)$} $line x key value]} {
		lappend state(meta) $key [string trim $value]
	    } elseif {[regexp ^HTTP $line]} {
		set state(http) $line
	    }
	}
    } else {
	if {[catch {
	    if {[info exists state(-handler)]} {
		set n [eval $state(-handler) {$s $token}]
	    } else {
		set block [read $s $state(-blocksize)]
		set n [string length $block]
		if {$n >= 0} {
		    append state(body) $block
		}
	    }
	    if {$n >= 0} {
		incr state(currentsize) $n
	    }
	} err]} {
	    Finish $token $err
	} else {
	    if {[info exists state(-progress)]} {
		eval $state(-progress) \
			{$token $state(totalsize) $state(currentsize)}
	    }
	}
    }
}

# http::CopyStart
#
#	Error handling wrapper around fcopy
#
# Arguments
#	s	The socket to copy from
#	token	The token returned from http::geturl
#
# Side Effects
#	This closes the connection upon error

proc http::CopyStart {s token} {
    variable $token
    upvar 0 $token state
    if {[catch {
	fcopy $s $state(-channel) -size $state(-blocksize) -command \
	    [list http::CopyDone $token]
    } err]} {
	Finish $token $err
    }
}

# http::CopyDone
#
#	fcopy completion callback
#
# Arguments
#	token	The token returned from http::geturl
#	count	The amount transfered
#
# Side Effects
#	Invokes callbacks

proc http::CopyDone {token count {error {}}} {
    variable $token
    upvar 0 $token state
    set s $state(sock)
    incr state(currentsize) $count
    if {[info exists state(-progress)]} {
	eval $state(-progress) {$token $state(totalsize) $state(currentsize)}
    }
    # At this point the token may have been reset
    if {[string length $error]} {
	Finish $token $error
    } elseif {[catch {eof $s} iseof] || $iseof} {
	Eof $token
    } else {
	CopyStart $s $token
    }
}

# http::Eof
#
#	Handle eof on the socket
#
# Arguments
#	token	The token returned from http::geturl
#
# Side Effects
#	Clean up the socket

proc http::Eof {token} {
    variable $token
    upvar 0 $token state
    if {[string equal $state(state) "header"]} {
	# Premature eof
	set state(status) eof
    } else {
	set state(status) ok
    }
    set state(state) eof
    Finish $token
}

# http::wait --
#
#	See documentaion for details.
#
# Arguments:
#	token	Connection token.
#
# Results:
#        The status after the wait.

proc http::wait {token} {
    variable $token
    upvar 0 $token state

    if {![info exists state(status)] || [string length $state(status)] == 0} {
	# We must wait on the original variable name, not the upvar alias
	vwait $token\(status)
    }

    return $state(status)
}

# http::formatQuery --
#
#	See documentaion for details.
#	Call http::formatQuery with an even number of arguments, where 
#	the first is a name, the second is a value, the third is another 
#	name, and so on.
#
# Arguments:
#	args	A list of name-value pairs.
#
# Results:
#        TODO

proc http::formatQuery {args} {
    set result ""
    set sep ""
    foreach i $args {
	append result $sep [mapReply $i]
	if {[string equal $sep "="]} {
	    set sep &
	} else {
	    set sep =
	}
    }
    return $result
}

# http::mapReply --
#
#	Do x-www-urlencoded character mapping
#
# Arguments:
#	string	The string the needs to be encoded
#
# Results:
#       The encoded string

proc http::mapReply {string} {
    variable formMap
    variable alphanumeric

    # The spec says: "non-alphanumeric characters are replaced by '%HH'"
    # 1 leave alphanumerics characters alone
    # 2 Convert every other character to an array lookup
    # 3 Escape constructs that are "special" to the tcl parser
    # 4 "subst" the result, doing all the array substitutions

    regsub -all \[^$alphanumeric\] $string {$formMap(&)} string
    regsub -all {[][{})\\]\)} $string {\\&} string
    return [subst -nocommand $string]
}

# http::ProxyRequired --
#	Default proxy filter. 
#
# Arguments:
#	host	The destination host
#
# Results:
#       The current proxy settings

proc http::ProxyRequired {host} {
    variable http
    if {[info exists http(-proxyhost)] && [string length $http(-proxyhost)]} {
	if {![info exists http(-proxyport)] || \
		![string length $http(-proxyport)]} {
	    set http(-proxyport) 8080
	}
	return [list $http(-proxyhost) $http(-proxyport)]
    }
}

#############################

proc copy_file_from_tftp {server file destination} {
    global errorInfo
    global autoconf_debug

    if [catch {cli_open} result] {
        error $result $errorInfo
    } else {
        array set cli1 $result
    }
    if [catch {cli_exec $cli1(fd) "enable"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "configure terminal"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "file prompt quiet"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "end"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "copy tftp://$server/$file $destination"} \
        result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "configure terminal"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "no file prompt quiet"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "end"} result] {
        error $result $errorInfo
    }
    if [catch {cli_close $cli1(fd) $cli1(tty_id)} result] {
        error $result $errorInfo
    }

    if {$autoconf_debug == 1} {
        puts "copied $server $file to $destination"
    }
}


proc copy_to_running {server file} {
    global errorInfo
    global autoconf_debug

    if [catch {cli_open} result] {
        error $result $errorInfo
    } else {
        array set cli1 $result
    }
    if [catch {cli_exec $cli1(fd) "enable"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "configure terminal"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "file prompt quiet"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "end"} result] {
        error $result $errorInfo
    }
    if [catch {cli_write $cli1(fd) "copy tftp://$server/$file running"} \
        result] {
        error $result $errorInfo
    }

    if [catch {cli_read_pattern $cli1(fd) "(#|>)"} result] {
        error $result $errorInfo
    }

    if [catch {cli_exec $cli1(fd) "configure terminal"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "no file prompt quiet"} result] {
        error $result $errorInfo
    }
    if [catch {cli_exec $cli1(fd) "end"} result] {
        error $result $errorInfo
    }
    if [catch {cli_close $cli1(fd) $cli1(tty_id)} result] {
        error $result $errorInfo
    }

    if {$autoconf_debug == 1} {
        puts "copied $server $file to running-config"
    }
}


if {[info exists _stat_debug]} {
    set stat_debug 1
} else {
    set stat_debug 0
}


# 2. Gather interface and version information from CLI
if [catch {cli_open} result] {
    error $result $errorInfo
} else {
    array set cli1 $result
}
if [catch {cli_exec $cli1(fd) "enable"} result] {
    error $result $errorInfo
}
if [catch {cli_exec $cli1(fd) "show mem stat"} memstats] {
    error $memstats $errorInfo
}

set foundmatch 0
foreach line [split $memstats \n] {
    set match1 [regexp {Processor\s+\S+\s+[0-9]+\s+([0-9]+)\s+([0-9]+).*} $line match memused memfree]
    if {$match1 == 1} {
        set foundmatch 1
        continue
    }
}
if {$stat_debug == 1} {
    if {$foundmatch == 1} {
       puts "Found memused: $memused"
       puts "Found memfree: $memfree"
    } else {
       puts "Unable to find memory usage"
    }
}

if [catch {cli_exec $cli1(fd) "show proc cpu | inc CPU utilization"} cpustats] {
    error $cpustats $errorInfo
}
set foundmatch 0
foreach line [split $cpustats \n] {
    set match1 [regexp {CPU utilization for five seconds: ([0-9]+).*one minute: ([0-9]+).*five minutes: ([0-9]+).*} $line match fivesec onemin fivemin]
    if {$match1 == 1} {
        set foundmatch 1
        continue
    }
}

if {$stat_debug == 1} {
    if {$foundmatch == 1} {
       puts "Found fivesecond: $fivesec"
       puts "Found onemin: $onemin"
       puts "Found fivemin: $fivemin"
    } else {
       puts "Unable to find CPU usage"
    }
}


if [catch {cli_exec $cli1(fd) "show env | inc temp"} tempstats] {
    error $tempstats $errorInfo
}

set foundinternalmatch 0
set foundcpumatch 0
set foundintakematch 0
set foundbackplanematch 0
foreach line [split $tempstats \n] {
    set match1 [regexp {Internal-ambient temperature = ([0-9]+), ([a-zA-Z]+).*} $line match internaltemp internaltempstr]
    if {$match1 == 1} {
        set foundinternalmatch 1
        continue
    }

    set match1 [regexp {CPU temperature = ([0-9]+), ([a-zA-Z]+).*} $line match cputemp cputempstr]
    if {$match1 == 1} {
        set foundcpumatch 1
        continue
    }

    set match1 [regexp {Intake temperature = ([0-9]+), ([a-zA-Z]+).*} $line match intaketemp intaketempstr]
    if {$match1 == 1} {
        set foundintakematch 1
        continue
    }

    set match1 [regexp {Backplane temperature = ([0-9]+), ([a-zA-Z]+).*} $line match backplanetemp backplanetempstr]
    if {$match1 == 1} {
        set foundbackplanematch 1
        continue
    }

}

if {$stat_debug == 1} {
    if {$foundinternalmatch == 1} {
       puts "Found Internal: $internaltemp, $internaltempstr"
    } else {
       puts "Unable to find internal temp"
    }
    if {$foundcpumatch == 1} {
       puts "Found CPU: $cputemp, $cputempstr"
    } else {
       puts "Unable to find CPU temp"
    }
    if {$foundintakematch == 1} {
       puts "Found Intake: $intaketemp, $intaketempstr"
    } else {
       puts "Unable to find Intake temp"
    }
    if {$foundbackplanematch == 1} {
       puts "Found Backplane: $backplanetemp, $backplanetempstr"
    } else {
       puts "Unable to find Backplane temp"
    }
}


if [catch {cli_exec $cli1(fd) \
      "show ip int brief | include up                    up"} upstats] {
    error $cli_show_up $errorInfo
}

set upinterfaces ""
foreach line [split $upstats \n] {
    set match1 [regexp {(\S+)\s+.*} $line match intf]
    if {$match1 == 1} {
        if {$upinterfaces == ""} {
           set upinterfaces $intf
        } else {
           append upinterfaces "||$intf"
        }
        continue
    }
}

if [catch {cli_close $cli1(fd) $cli1(tty_id)} result] {
    error $result $errorInfo
}

if {[catch {context_retrieve "statistics" context_stats} context_stats]} {
    # No context found
    if {$stat_debug >= 1} {
        puts "no context found"
    }
    unset context_stats
} else {
    if {$stat_debug >= 1} {
        puts "Context found: $context_stats"
    }
}


if {[info exists _stat_changes]} {
    if {$_stat_changes == 1} {
        if {[info exists context_stats]} {
            if {$stat_debug >= 1} {
                puts "Last Statistics Read: $context_stats"
            }

            ## Compare stats here

            foreach entry [split $context_stats " "] {
                set name "c_"
                append name [lindex [split $entry :] 0]
                set value [lindex [split $entry :] 1]
                eval "set $name $value"
            }

            set memusedchanged [expr $memused - $c_memused]
            set fivesecchanged [expr $fivesec - $c_fivesec]
            set oneminchanged [expr $onemin - $c_onemin]
            set fiveminchanged [expr $fivemin - $c_fivemin]
            if {[info exists internaltemp]} {
               set internaltempchanged [expr $internaltemp - $c_internaltemp]
               set cputempchanged [expr $cputemp - $c_cputemp]
               set intaketempchanged [expr $intaketemp - $c_intaketemp]
               set backplanetempchanged [expr $backplanetemp - $c_backplanetemp]
               puts "Change in Temp: Internal: $internaltempchanged CPU: $cputempchanged Intake: $intaketempchanged Backplane: $backplanetempchanged"
            }
            puts "Change in Memory Used: $memusedchanged"
            puts "Change in CPU: Five second: ${fivesecchanged}% One minute: ${oneminchanged}% Five minute: ${fiveminchanged}%"

            foreach intf [split $c_upinterfaces "||"] {
                set match1 [regexp $intf $upinterfaces match]
                if {$match1 == 0} {
                    puts "Change in Interface: $intf is no longer up"
                }
            }    
        }
    }
}


#Fill in new stats for context save: set context_stats ...

if {[info exists internaltemp]} {
     set context_stats "memused:$memused memfree:$memfree fivesec:$fivesec onemin:$onemin fivemin:$fivemin internaltemp:$internaltemp internaltempstr:$internaltempstr cputemp:$cputemp cputempstr:$cputempstr intaketemp:$intaketemp intaketempstr:$intaketempstr backplanetemp:$backplanetemp backplanetempstr:$backplanetempstr upinterfaces:$upinterfaces"
} else {
     set context_stats "memused:$memused memfree:$memfree fivesec:$fivesec onemin:$onemin fivemin:$fivemin upinterfaces:$upinterfaces"
}

context_save "statistics" context_stats

#Determine URL location to send info to.
if {[info exists _statcoll_url]} {
    set postUrl $_statcoll_url
} else {
    action_syslog priority info msg \
        "EEM environment variable _statcoll_url not set, exiting"
    return
}

set ourhost [info hostname]

if {$stat_debug == 1} {
    action_syslog priority info msg "Using autoconf URL: $postUrl"
}

for {set i 0} {($i < 25) && \
    [catch {http::geturl $postUrl -query "hostname:$ourhost $context_stats" -queryblocksize 50 -type \
            "text/plain" } token]} {incr i} {
    after 2000
}

if {$stat_debug == 1} {
    action_syslog priority info msg \
        "Response from URL: [http::data $token]"
}

# 6. if the transmission to the autoconf site was successful,
#    log a message
if {$i < 5} {
    if {[http::error $token] == ""} {

        foreach line [split [http::data $token] \n] {
            # puts "line back is $line"
        }
    }
    http::Finish $token
    http::cleanup $token
} else {
    action_syslog priority notice msg "tm_sendstats delivery failed"
    http::Finish $token
    http::cleanup $token
}
