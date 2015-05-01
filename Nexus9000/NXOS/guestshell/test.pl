#!/usr/bin/perl

print <<EOF;
   
   Hello! This is a perl script.

EOF


print "My neighbors are:\n";
$ver = `dohost --exec "show cdp neigh"`;
$found_start = 0;
foreach $line (split('\n', $ver)) {
   if ($found_start == 1) {
       @values = split(/\s+/, $line);
       next if $values[0] eq ""; 
       $vd{$values[0]}++
   } else {
      if ($line =~ /Device-ID/) {
          $found_start = 1;
      }
   }
}

foreach $entry (keys(%vd)) {
   print "   $entry\n";
}
