#matching,ipl,ebl,rules,selected,general audience,formal,text cat,xtraction,collab,app

open(D,"<papers.dat") || die;
@db = ();
while (<D>) {
  chop;
  push(@db,$_);
}


%topic = ('m', 'Matching/Data Integration',
	  't', 'Text Categorization',
	  'x', 'Information Extraction',
	  'r', 'Rule Learning',
	  'c', 'Collaborative Filtering',
	  'a', 'Applications',
	  'f', 'Formal Results',
	  'i', 'Inductive Logic Programming',
	  'e', 'Explanation-Based Learning',
);
%form = ('word', 'Microsoft Word - with apologies for the portability issues',
	 'ps', 'Postscript',
	 'pdf', 'PDF',
	 'html', 'HTML');

@keys = qw(m t r e f i x c a);

#selected
open(H,">../pubs-s.html") || die;
&header("Selected and/or recent papers by William W. Cohen");
&bib('s','');
&footer;
close(H);
#by topic
foreach $k (@keys) {
  open(H,">../pubs-$k.html") || die;
  &header("William W. Cohen's Papers: $topic{$k}");
  &bib($k,'');
  &footer;
  close(H);
}
#by year
open(H,">../pubs.html") || die;
&header("Papers by William W. Cohen");
foreach $p (@db) {
  ($dummy,$yr) = split(/\|/,$p);
  $years{$yr}++;
}
foreach $yr (sort {$b <=> $a} keys(%years)) {
  print H "<h3>$yr</h3>\n";
  &bib('',$yr);
}
&footer;
close(H);

#show header
sub header {
  my($title) = @_;
  print H "<html><head><title>$title</title></head>\n";
  print H "<body><h3>$title</h3>\n";
}

sub footer {
  print H "<p align=\"center\">[";
  print H "<a href=\"pubs-s.html\">Selected papers</a>";
  print H "| By topic:";
  foreach $k1 (@keys) {
    print H " <a href=\"pubs-$k1.html\">$topic{$k1}</a>| ";
  }
  print H " By year: <a href=\"pubs.html\">All papers</a>]</p>";
  #print H "<hr>\n\n<!--#easybanner4-->\n";
  print H "</body></html>\n";
}

#show a bibliography list
sub bib {
  my($k,$theyear) = @_;
  print H "<ul>\n";
  foreach $p (@db) {
    &bib1($k,$p,$theyear);
  }
  print H "</ul>\n";
}

#show a single bibliography listing
sub bib1 {
  my($k,$p,$theyear) = @_;
  ($cats,$year,$author,$title,$book,$url,$format) = split(/\|/,$p);    
  next unless ($cats =~ m/$k/);
  next if $theyear && ($year != $theyear);
  ($it,@nonits) = split(/,/,$book); 
  $nonit = join('',@nonits);
  $nonit = ", $nonit" if $nonit=~/\S/;
  $format = $form{$format} if ($form{$format}); 
  print H "<li>$author, ";
  if ($url=~/\S/) {
    print H "<a href=\"$url\"><i>$title</i></a> ($format),\n"; 
  } else {
    print H "<i>$title</i> (not available online),\n"; 
  }
  if ($it =~ /\bsubmitted\b/) {
    print H "<i>$it</i>$nonit";
  } else {
    print H "in <i>$it</i>$nonit";
  }
  print H " ($year)" unless $theyear;
  print H ".\n</li>\n";
}

