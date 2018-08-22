#!/usr/bin/perl

##############################################################################
#build a javascript "dictionary" game 
#
# - document expected directories, files, etc
# 
##############################################################################

$Debug=1;

#mime types
@Image = ('gif','jpeg','jpg','jpe');
@Sound = ('au','snd','wav');
@Video = ('mpeg','mpg','mpe','qt','mov','avi');
@Text = ('txt','text');

$Root = "/home/wcohen/dict/stuff";
chdir($Root) || die("can't cd to $Root");
$Lib  = "_lib";

#standard buttons/sounds
$Videof = &mimefile("$Lib/amovie",@Image);
$Soundf = &mimefile("$Lib/asound",@Image);
$Booksf = &mimefile("$Lib/abooks",@Image);
$Weblinkf = &mimefile("$Lib/awww",@Image);
$Blankf = &mimefile("$Lib/ablank",@Image);
$Video_button = $Videof ? "<img src=\"$Videof\">" : "Video" ;
$Sound_button = $Soundf ? "<img src=\"$Soundf\">" : "Sound" ;
$Books_button = $Booksf ? "<img src=\"$Booksf\">" : "Other Dictionaries" ;
$Link_button = $Weblinkf ? "<img src=\"$Weblinkf\">" : "See Also" ;

$Gooff  = &mimefile("$Lib/agoof",@Sound);
print STDERR "warning - no goof file!\n" unless $Gooff;
$Introf  = &mimefile("$Lib/aintro",@Sound);
print STDERR "warning - no intro file!\n" unless $Introf;
$Clickf = &mimefile("$Lib/aclick",@Sound) || &mimefile("$Lib/agoof",@Sound);

#find a file of designated type
sub mimefile
{
    local($stem,@exts) = @_;
    foreach $ext (@exts) {
	return "$stem.$ext" if (-e "$stem.$ext");
    }
    return "";
}

#find all files of designated type
sub mimefiles
{
    local($stem,@exts) = @_;
    local($f,@files);

    foreach $ext (@exts) { 
	while ($f = <$stem*.$ext>) {
	    push(@files,$f) if ($f =~ /$stem\d*\.$ext/);
	}
    }
    return @files;
}

#return text of a file
sub filetext
{
    local($file,$default,$str) = @_;
    local(@tmp);
    return $default unless $file; 
    open(TEXT,$file) || return $default;
    @tmp = <TEXT>;
    close(TEXT);
    $str = join('',@tmp);
    $str =~ tr/\n/ /;
    return $str;
}

#a form to produce a sound
sub soundform 
{
    local($form,$file) = @_;
    #seems to need at least one input somewhere...
    "<form name=\"$form\" action=\"$file\"><input type=\"hidden\"></form>"; 
}

#convert a word into text appropriate for a dictionary entry
sub wordtext
{
    local($word) = @_;
    $text = $word; 
    $text =~ s/_/ /go; 
    $text =~ tr/[a-z]/[A-Z/; 
    $text;		       
}

sub capitalize
{
    local($text) = @_;
    $text =~ s/^(.)/\<font size=\+3\>$1\<\/font\>/;
    $text;
}
