##############################################################################
# Usage: perl makepubs.pl [mac]
#
#
# publication codes: Journal, Conference,
#topic codes
%topic = ('m', 'Matching/Data Integration',
	  't', 'Text Categorization',
	  'x', 'Info Extraction/Reading',
	  'l', 'Topic Modeling',
	  'g', 'Learning in Graphs',
	  'd', 'Intelligent Tutoring',
	  'r', 'Rule Learning',
	  'c', 'Collaborative Filtering',
	  'a', 'Applications',
	  'f', 'Formal Results',
	  'i', 'Inductive Logic Programming',
	  'e', 'Explanation-Based Learning',
	  'n', 'Deep Learning',
	  'G', 'GNAT System',
);
@keys = qw(n x l g m t r e f i c a d G);

$thisYear = 2020;
$os = shift || 'unix';
print "os is $os\n";

##############################################################################
#load the pub database
open(F,"<pubs.dat") || die;
while ($line = <F>) {
  ($a1,$a2,$yr,$file,$cite,$thread) = split(/\|/,$line);
  chomp($cite);
  chop($auth = <F>);
  chop($title = <F>);
  chop($id = <F>);
  $sepPlusComment = <F>;  #skip separator

  $file = 'NONE' unless $file;

  ############################# create entry
  
  $bibEntry = "$auth ($yr): " . &hlink("postscript/$file",$title) . " in " . &hlink($id,$cite);
  if ($sepPlusComment =~ /\!\!/) {
      ($sep,$comment) = split(/\!\!\s*/,$sepPlusComment);
      chomp($comment);
      $bibEntry .= " <b>($comment)</b>";
  }
  $attrib{$bibEntry} = $a2;
  $year{$bibEntry} = $yr;
  $someYear{$yr}++;
  #stuff for rss feed
  $bibFile{$bibEntry} = "postscript/$file" unless $file=~/https?/;
  $bibTitle{$bibEntry} = $title;
  $bibVenue{$bibEntry} = $cite;
  $bibAuth{$bibEntry} = $auth;

  #################### handle threads
  
  push(@bib,$bibEntry); 

#  if ($thread !~ /\S/) {
#    $thread = '';
#  }
#  if ($thread) {
#      print "thread $thread contains [$yr $file $cite]\n";
#  }

  # thread stuff is broken?
#  if (!$thread || $thread!~/.in/) {
#    print "pushing [$yr $file $cite]\n";
#
#  } elsif ($thread =~ /\.end/) {
#    print "$thread is end [$yr $file $cite]\n";
#    ($t,$dummy) = split(/\./,$thread);
#    $root{$t} = $bibEntry;
#  } elsif ($thread =~ /\.in/) {
#    print "$thread is in [$yr $file $cite]\n";
#    ($t,$dummy) = split(/\./,$thread);
#    $r = $root{$t};
#    $earlier{$r} .= "; " if $earlier{$r};
#    $earlier{$r} .= $bibEntry;
#  }

}

print "loaded ",scalar(@bib)," entries\n";

#################### make web site

# selected papers
open(H,">../pubs-s.html") || die;
&header("Selected and/or recent papers by William W. Cohen");
foreach my $y ($thisYear,$thisYear-1,$thisYear-2) {
  &subheader("Recent papers: $y");
  #&bib('and',$y,$y,'^[^s]*$');
  &bib('and',$y,$y,'');
}
&subheader("Selected other papers");
&bib('and',0,$thisYear-3,'s');
&footer;
close(H);

#by topic
foreach $k (@keys) {
  open(H,">../pubs-$k.html") || die;
  &header("William W. Cohen's Papers: $topic{$k}");
  &bib('and',0,9999,$k);
  &footer;
  close(H);
}

#by year
open(H,">../pubs.html") || die;
&header("Papers by William W. Cohen");
foreach $yr (sort {$b <=> $a} keys(%someYear)) {
  print H "<h3>$yr</h3>\n";
  &bib('and',$yr,$yr,'');
}
&footer;
close(H);

#rss feed in atom forma
open(H,">../pubs-atom.xml") || die;
print H '<?xml version="1.0" encoding="utf-8"?>',"\n";
print H '<feed xmlns="http://www.w3.org/2005/Atom">',"\n";
print H '  <title> Publications of William W. Cohen</title>',"\n"; 
print H '  <link rel="self" href="http://www.cs.cmu.edu/~wcohen/pubs-atom.xml"/>',"\n";
chop(my $timestamp = `date +%G-%m-%dT%H:%M:%SZ`);
print H "  <updated>$timestamp</updated>\n";
print H "  <published>$timestamp</published>\n";
print H '  <author><name>William W. Cohen</name></author>',"\n"; 
print H '  <id>http://wcohen.com/pubs-rss.xml</id>',"\n";
foreach $bibEntry (@bib) {
    my $url = $bibFile{$bibEntry};
    next unless $url;
    next if $url =~ /NONE/;
    my $title = $bibTitle{$bibEntry};
    my $venue = $bibVenue{$bibEntry};
    my $year = $year{$bibEntry};
    my $auth = $bibAuth{$bibEntry};
    $auth =~ s/\&/\&amp\;/g;
    $venue =~ s/\&/\&amp\;/g;
    #default to 
    my $fileTime;
    if ($os eq 'mac') {
	chop(my $fileTime = `date -j -f %Y-%m-%d $year-01-01 +%G-%m-%dT%H:%M:%SZ`);	
    } elsif ($os eq 'unix') {
	chop(my $fileTime = `date -d $year-01-01 +%G-%m-%dT%H:%M:%SZ`);	
    } else {
	die "unknown os $os";
    }
    if ($url =~ /^postscript/ && $os eq 'unix' && $file ne 'NONE') {
	chop($fileTime = `date -r ../$url +%G-%m-%dT%H:%M:%SZ`);
    }
    print H "  <entry>\n";
    print H "    <title>$title</title>\n";
    print H "    <link href=\"http://wcohen.com/$url\"/>\n";
    print H "    <id>http://wcohen.com/$url</id>\n";
    print H "    <updated>$fileTime</updated>\n";
    print H "    <summary>$title by $auth: Published $year in $venue</summary>\n";
    print H "  </entry>\n";
}
print H "</feed>\n";
close(D);

#show header
sub header {
  my($title) = @_;
  print H "<html><head><title>$title</title>\n";
  print H "<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\"/>\n";
  print H "</head>\n";
  print H "<body><h3>$title</h3>\n";
#  print H "<h4><a href=\"http://www.cs.cmu.edu/~wcohen/pubs-atom.xml\">[RSS feed]</a></h4>\n";
}

sub subheader {
  my($hdr) = @_;
  print H "<h3>$hdr</h3>\n";
}

sub footer {
  print H "<p align=\"center\">[";
  print H "<a href=\"pubs-s.html\">Selected papers</a>";
  print H "| By topic:";
  foreach $k1 (@keys) {
    print H " <a href=\"pubs-$k1.html\">$topic{$k1}</a>| ";
  }
  print H " By year: <a href=\"pubs.html\">All papers</a>";
  #print H "| <a href=\"http://www.dapper.net/transform.php?dappName=WilliamCohenspublications&transformer=RSS&extraArg_title=Title&applyToUrl=http%3A%2F%2Fwww.cs.cmu.edu%2F~wcohen%2Fpubs.html\">RSS</a>]</p>\n";
  print H "]</p>\n";

  #print H "<hr>\n\n<!--#easybanner4-->\n";
  print H '<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">',"\n"; 
  print H "</script>\n";
  print H '<script type="text/javascript">',"\n";
  print H '_uacct = "UA-2090677-1;',"\n";
  print H "urchinTracker();\n";
  print H "</script>\n";
  print H "</body></html>\n";
}

#show a bibliography list
sub bib {
  my($op,$loYear,$hiYear,$k) = @_;
  print H "<ol>\n";
  foreach $bibEntry (@bib) {
    $y = $year{$bibEntry};
    #print $bibEntry,"\n";
    #print "filter $loYear<=$y<=$hiYear $op ",$attrib{$bibEntry},"=~/$k/";
    if ($op eq 'or') {
      if (($attrib{$bibEntry}=~/$k/) || ($y>=$loYear && $y<=$hiYear)) {
	&bib1($bibEntry); 
	#print " - pass\n";
      } else {
	#print " - fail\n";
      }
    } else {
      if (($attrib{$bibEntry}=~/$k/) && ($y>=$loYear && $y<=$hiYear)) {
	&bib1($bibEntry);
	#print "- pass\n";
      } else {
	#print " - fail\n";
      }
    }
  }
  print H "</ol>\n";
}

#show a single bibliography listing
sub bib1 {
  my($be) = @_;
  print H "<li>$be";
  print H ". <font size=-1>(Originally published as: ",$earlier{$be},")</font>" if $earlier{$be};
  print H ".\n</li>\n";
}

sub hlink {
  my($href,$anchorText) = @_;
  if ($href=~/NONE/ || $href=~/DBLP-id/) {
    return "<i>$anchorText</i>";
  } elsif ($href=~m[postscript/(https?://.*)]) {
    return '<a href="' . $1 . '">' . $anchorText . '</a>' ;
  } else {
    return '<a href="' . $href . '">' . $anchorText . '</a>' ;
  }
}

