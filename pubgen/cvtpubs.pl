##############################################################################
#load the pub database

open(F,"<pubs.dat") || die;
print "[\n";
$k = 0;
while ($line = <F>) {
  $k++;
  ($a1,$a2,$yr,$file,$cite,$thread) = split(/\|/,$line);
  chomp($thread);
  chomp($cite);
  chop($auth = <F>);
  chop($title = <F>);
  chop($id = <F>);
  $sepPlusComment = <F>;  #skip separator
  if ($sepPlusComment =~ /\!\!/) {
      ($sep,$comment) = split(/\!\!\s*/,$sepPlusComment);
      chomp($comment);
  } elsif ($sepPlusComment =~ /\#\#/) {
      ($sep,$comment) = split(/\#\#\s*/,$sepPlusComment);
      chomp($comment);
  } else {
    $comment = '';
  }
  $cite =~ s/"/\\"/g;
  $title =~ s/"/\\"/g;
  $comment =~ s/"/\\"/g;

  print ",\n" if $k>1;
  print "  {\n";
  print "    \"title\": \"$title\",\n";
  print "    \"authors\": \"$auth\",\n";
  print "    \"venues\": \"$a1\",\n";
  print "    \"year\": \"$yr\",\n";
  print "    \"topics\": \"$a2\",\n";
  print "    \"url\": \"$file\",\n";
  print "    \"cite\": \"$cite\",\n";
  print "    \"thread\": \"$thread\",\n";
  print "    \"doi\": \"$id\",\n";
  print "    \"comment\": \"$comment\"\n";
  print "  }";
}
print "\n]\n";
