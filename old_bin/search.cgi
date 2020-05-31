#!/usr/bin/perl

#http://www.boutell.com/search/
#
#CHANGE THE ABOVE SETTING TO WHERE PERL5 IS ON YOUR COMPUTER
#usually /usr/local/bin/perl.

#CHANGE THIS TO THE URL WHERE YOUR WEB SPACE IS
$baseurl = "http://sdss3.apo.nmsu.edu/sdssProcedures";

#CHANGE THIS TO THE DIRECTORY WHERE YOUR WEB SPACE IS
$filepath = "/usr/local/www/html/sdssProcedures";

#CHANGE THIS TO THE FILE CONTAINING YOUR SEARCH INDEX,
#created with search-index, WHICH MUST BE RUN **OFTEN**
$indexFile = "searchindex.txt";

use CGI;
$query = new CGI;

chdir($filepath);

$target = $query->param('target');
if ($target eq "") {
	&header;
	&form;
	&footer;
	exit 0;
}
$rule = $query->param('rule');

# Simple HTML flusher
$target =~ s/\<.*?\>//g;
# Case insensitive
$target =~ tr/A-Z/a-z/;
# If it's not a letter, it's whitespace
$target =~ s/[^a-z]/ /g;

@words = split(/ /, $target);
if (open(IN, $indexFile)) {
	while ($line = <IN>) {
		my($wordCount, $score);
		if ($line =~ /^(\S+) /) {
			$filename = $1;
		} else {
			next;
		}
		for $w (@words) {
			if ($line =~ /(\d+):$w/)
			{ 
				$score += $1;
				$wordCount ++;
			}
		}
		if ($rule eq "and") {
			if ($wordCount == int(@words)) {
				push @files, "$score:$filename";
			}	
		} elsif ($wordCount > 0) {
			push @files, "$score:$filename";
		}
	}
}

&header;
if (!int(@files)) {
	print "<h3>Sorry, no pages were found.\n</h3>\n";
} else {
	print "<h3>The following pages were found:</h3>\n";
}
print "<ul>\n";

@files = sort {$b <=> $a} @files;

for $n (@files) {
	my($score, $file) = split(/:/, $n);
# Skip forbidden pages. These examples work well for our site.
#	if ($file =~ /\/usage/) {
#		next;
#	}
#	if ($file =~ /\/wusage\/example/) {
#		next;
#	}
	$title = "";
	$data = "";
	if (open(IN, "$filepath$file")) {
		while ($line = <IN>) {
			$data .= $line;
			if ($data =~ /<title>\s*(.*)\s*\<\/title>/i) {
				$title = $1;
				last;
			}
		} 
		close(IN);
	}
	if ($title eq "") {
		$title = "$file";
	}
	print "<li>$score: <a href=\"$baseurl$file\">$title<\/a>\n";
}
print "</ul>\n";
print "<hr>\n";
&form;
&footer;

sub header
{
	print "Content-type: text/html\n\n";
	&template("before-head");
	print "<title>Search sdssProcedures</title>\n";
	&template("after-head");
	&template("before-body");
	print "<h1>Search sdssProcedures</h1>\n";
}

sub footer
{
	&template("after-body");
}

sub template
{
        my($file) = @_;
        open(IN, "/home/admin/html/$file");
        while ($line = <IN>) {
                print $line;
        }
        close(IN);
}

sub form
{
	print <<EOM
Enter one or more words to look for.
<p>
<form action="/cgi-bin/search.cgi" method="GET">
Return pages containing
<select name="rule">
<option value="and">ALL
<option value="any">ANY
</select>
of these words: 
<input name="target">
<input type="submit" value="Go!">
</form>
<p>
<a href="http://www.boutell.com/search/"><em>FREE:</em> You can have this search facility
on your own site!</a>
EOM
;
}


