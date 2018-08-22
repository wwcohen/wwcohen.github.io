#!/usr/local/bin/perl

##############################################################################
#build a speller
##############################################################################

$Debug=1;

@Words = ('FOO','FAZE','FOOL','FAD','BAR','BAT');
@Letters = ('A','B','C','D','E','F','G',
	    'H','I','J','K','L','M','N',
	    'O','P','Q','R','S','T','U',
	    'V','W','X','Y','Z');

foreach $w (@Words) {
	$Isword{$w} = 1;
}
&trie("",@Words);

sub trie
{
	local($pref,@suffs) = @_;
	local(%cont);
	print "pref: $pref\n";
	print "suff: ",join(' ',@suffs),"\n"; 

	foreach $a (@Letters) {
		@nsuff = grep(/^$a/,@suffs);
		@nsuff = grep(s/^$a//,@nsuff);
		if (@nsuff) {
			$ncont++;
			$cont{$a} = 1;
			&trie($pref.$a, @nsuff);
		}		
	}
	&kb($pref,*cont); 	
}

sub kb
{
	local($pref,*mark) = @_;
	local($prev,$loadact); 

	if ($pref) {
		($prev) = ($pref =~ /(.*)./); 
	} else {
		$prev = "";
	}
	if ($Isword{$pref} || $pref eq "") {
		$loadact = "v('$pref')";
	}  else {
		$loadact = "n('beep.au')";
	}

	open(KB,">kb$pref.html") || die("can't write bk$pref.htlm");
	print KB <<END_HEADER;
<html>
<script language="JavaScript">
<!-- hiding
   function n(url) {
	document.noiseform.action = url;
	document.noiseform.submit();
	return 1;
   }
   function v(url) {
        parent.view.document.viewout.display.value=url;
	return 1;
   }
// -->
</script>
<head>
<title>Spell</title>
</head>
<body onLoad="$loadact">
<hr>
<form name="kb">
<h1 align=center>
  <input type="text" name="kbout" value="$pref"><br>
  <a href="kb$prev.html">[back]</a>
  <a href="kb.html">[clear]</a>
<it>
</h2>
<h2 align=center>
END_HEADER

	print "// printed header\n" if $Debug;

	@abc = ('A','B','C','D','E','F','G','br',
		'H','I','J','K','L','M','N','br',
		'O','P','Q','R','S','T','U','br',
		'V','W','X','Y','Z');

	sub randomly { rand() <=> 0.5; }

	foreach $a (@abc) {
	    if 	($a eq 'br') {
		print KB "<br>\n";
		next;
	    }
            if ($mark{$a}) {		
		print KB "<font size=+7>";
	        print KB "<a href=\"kb$pref$a.html\"> $a </a>";
		print KB "</font>";
            } else {
		print KB "<font>";
	        print KB "$a";
		print KB "</font>";
	    }		
	}
	print "// generated keyboard for prefix $pref\n" if $Debug;

	print KB <<END_FOOT;
</form>
</it>
</h2>
<form name="noiseform" action="clink.au"><input type="hidden"></form>
</body>
<html>
END_FOOT

}