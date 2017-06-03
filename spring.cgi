#!/usr/bin/perl
# calculate 911 spring plate angles
# 01/03/2002 Thom Fitzpatrick & Will Ferch

use strict 'refs';
use strict;
#use warnings;
use CGI qw(:standard);
#use CGI::Carp qw/fatalsToBrowser/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

my %ANGLE;
my $LOG="/var/www/vhosts/rennlight.com/www/cgi-bin/log/spring.log";

#print header();
print "Content-type: text/html\n\n";
print "<head>\n";
print "<link rel=stylesheet href=http://www.rennlight.com/rennlight.css TYPE=text/css>\n";
print "<meta name=description content='Thom Fitzpatrick Porsche 911 spring plate angle calculator - use this form to find the drop angle for your spring plates when installing 911 and 930 torsion bars.'>\n";
print "<meta name=keywords content='Porsche, 911, 930, rear suspension, torsion bar, spring plate, index, trailing arm, spring plate angle'>\n";
print title("911 Spring Plate Angle Calculator");
print "<body>\n";
print h4("911 Spring Plate Angle Calculator");

# if 'dist' isn't set, then (probably) no parameters are set; show form and exit
if (!param('dist')) {
	ShowForm();
	Trailer();
	print end_html;
	exit 0;
}

# load trig tables
LoadTrig();

# constant for torsion bar 911's
my $BAR_LENGTH="18.5";

# slurp values from form
my $weight=param('weight'); # weight we display
my $dist=param('dist');
my $f_static=param('static');
my $bar_size=param('bar_size');
my $w_units=param('w_units');

# display-only values
my $d_weight = $weight;
my $d_droop;
my $d_static;
my $d_total_droop;

# convert to pounds if necessary
if ($w_units eq "kg") {
	$weight = $weight * 2.2046;
} 

# sanity check
if ($weight == 0) {
	print "<h4><font color=red>Sorry, weight can't be zero!</font></h4>\n";
	ShowForm();
	print end_html;
	exit 0;
}

my ($static, $ride) = split (/:/, $f_static);
#print "static: $ride<br>\n";

# calc weight distribution
my ($pct_front,$pct_rear) = split(/:/, $dist);
my $front = ($pct_front / 100) * $weight;
my $rear = ($pct_rear / 100) * $weight;
my $fw = $front / 2;
my $rw = $rear / 2;

# calc droop
my ($size_mm,$spring_rate) = split(/:/, $bar_size);
my $droop = $rw / $spring_rate;
my $total_droop = $static + $droop;
my $sine = $total_droop / $BAR_LENGTH;

# do a lookup on trig table
my $angle;
my $last = 0;
foreach (sort keys %ANGLE) {
	# if the angle falls between the previous value and this value, we consider it a match
	if ($sine < $_ && $sine > $last) {
		$angle="$ANGLE{$last}°- $ANGLE{$_}°";
		last;
	}
	$last = $_;
}

# dump results
print "<center>\n";
print "<table border=1 width=30%>\n";
print "<tr>\n";
print "<th colspan=3><i>Vehicle Info</i></th>\n";
print "<tr>\n";
print "<th align=right>Weight of car</td>\n";
printf "<td colspan=2 align=center>%d<font size=-1>$w_units</td>\n", $d_weight;
print "</tr>\n";

print "<tr>\n";
print "<th align=right>Weight Distribution ($dist)</td>\n";
print "<th align=center>Front</td>\n";
print "<th align=center>Rear</td>\n";
print "</tr>\n";

print "<tr>\n";
print "<th align=right>Axle</td>\n";
printf "<td align=center>%d<font size=-1>$w_units</td>\n",$front;
printf "<td align=center>%d<font size=-1>$w_units</td>\n",$rear;
print "</tr>\n";

print "<tr>\n";
print "<th align=right>Wheel</td>\n";
printf "<td align=center>%d<font size=-1>$w_units</td>\n",$fw;
printf "<td align=center>%d<font size=-1>$w_units</td>\n",$rw;
print "</tr>\n";

print "</table>\n";

print "<p>\n";
print "<table border=1 width=30%>\n";

print "<tr>\n";
print "<th colspan=2><i>Spring Plate Angle Calculations</i></th>\n";
print "</tr>\n";

print "<tr>\n";
print "<th align=right>Torsion bar size</td>\n";
print "<td align=center>$size_mm<font size=-1>mm</td>\n";
print "</tr>\n";

print "<tr>\n";
print "<th align=right>Static ride height</td>\n";
printf "<!-- static: %.2f -->\n", $static;
print "<td align=center>$ride</td>\n";
print "</tr>\n";

printf "<!-- Weight-induced droop: %.2f -->\n", $droop;

print "<tr>\n";
print "<th align=right>Total droop</td>\n";
printf "<td align=center>%.2f\"</td>\n", $total_droop;
print "</tr>\n";

#print "<tr>\n";
#printf "<td align=right>Sine of free-hanging angle (%.2f / $BAR_LENGTH)</td>\n", $total_droop;
#printf "<td align=center>%.4f</td>\n", $sine;
#print "</tr>\n";

print "<tr>\n";
print "<th align=right>Spring Plate Angle</td>\n";
print "<td align=center bgcolor=yellow><b>$angle</td>\n";
print "</tr>\n";

print "</table>\n";
print "</center>\n";

print  "\n";
Log("$d_weight:$w_units:$size_mm:$static:$angle");
Trailer();

sub Trailer () {
print "<p>For a comprehensive explanation of the principles behind this calculation, please
see <a href=http://tech.rennlist.com/911/pdf/settings.pdf>Will Ferch's Rennlist Tech Article</a> on
the subject</p>\n";

print "<p>To set the spring plate angle, use one of these handy <a href=http://www.harborfreight.com/cpi/ctaf/Displayitem.taf?itemnumber=34214 target=_hf>Angle Finder</a> available from Harbor Freight and other tool stores.\n";

print "<p><center>\n";
print "<a href=http://rennlight.com/image/angle.jpg target=_img><img src=http://rennlight.com/image/_angle.jpg align=absmiddle></a>\n";
print "<a href=http://rennlight.com/image/raise-trailing-arm.jpg target=_img><img src=http://rennlight.com/image/_raise-trailing-arm.jpg align=absmiddle></a>\n";
print "</center>\n";

print  "<p>Thanks to <a href=mailto:WFerch911\@cs.com>Will Ferch</a> for doing the actual math that made this possible.\n</p>";

print "<p>Technical questions about this web page and/or script can be directed to <a href=mailto:thom\@calweb.com?SUBJECT=Spring%20Plate%20Calculator>Thom Fitzpatrick</a>\n";

print "<p><b><a href=http://rennlight.com><< Home</a></b>\n";

print end_html;

}

sub ShowForm () {
print <<EOF;
<form action=http://www.rennlight.com/cgi-bin/spring.cgi method=post>

<center>
<table border=1 width=40%>

<tr>
<td align = right>Weight of car <font size=-2>
<input type=radio name=w_units value=lbs checked>lbs
<input type=radio name=w_units value=kg>Kg
</font>
</td>
<td><input text name=weight size=5></td>
</tr>

<tr>
<td align = right>
<!--Static spring plate droop <font size=-2><br>(default is Euro height, in inches)-->
Desired ride height
</td>
<td>
<!--<input text name=static size=5 value="3.8"> -->
<select name=static size=1>
<option value="3.8:Euro">Euro ride height
<option value="4.55:USA">USA ride height
<option value="3.0:Race">Race ride height
<option value="2.5:Low-Rider">Low-rider Ghetto drop yo!
</select>
</td>
</tr>

<tr>
<td align=right>Rear torsion bar size</td>
<td>
<select name=bar_size size=1 > 
<option value="23:100">23mm
<option value="24:120">24mm
<option value="24.1:122">24.1mm
<option value="25:140">25mm
<option value="26:165">26mm
<option value="27:191">27mm
<option value="28:221">28mm
<option value="29:254">29mm
<option value="30:291">30mm
<option value="31:332">31mm
<option value="32:377">32mm
<option value="33:427">33mm
</select>
</td></tr>

<tr>
<td align=right>Weight distribution (front:rear)</td>
<td>
<select name=dist size=1 > 
<option value="40:60">40/60 (normal)
<option value="45:55">45/55 
<option value="38:62">38/62 (930?) 
<!--<option value="50:50">50/50-->
</select>

<tr>
<td colspan=2 align=center><input type="submit" value="Submit"> &nbsp; &nbsp;<input type="reset" value="Clear Form"></td>
</tr>
</table>
</center>
</form>

EOF
}

# hard-code trig table into hash
sub LoadTrig () {
	$ANGLE{0.000000} = 0; 
	$ANGLE{0.017452} = 1; 
	$ANGLE{0.034899} = 2; 
	$ANGLE{0.052336} = 3; 
	$ANGLE{0.069756} = 4; 
	$ANGLE{0.087156} = 5; 
	$ANGLE{0.104528} = 6; 
	$ANGLE{0.121869} = 7; 
	$ANGLE{0.139173} = 8; 
	$ANGLE{0.156434} = 9; 
	$ANGLE{0.173648} = 10; 
	$ANGLE{0.190809} = 11; 
	$ANGLE{0.207912} = 12; 
	$ANGLE{0.224951} = 13; 
	$ANGLE{0.241922} = 14; 
	$ANGLE{0.258819} = 15; 
	$ANGLE{0.275637} = 16; 
	$ANGLE{0.292372} = 17; 
	$ANGLE{0.309017} = 18; 
	$ANGLE{0.325568} = 19; 
	$ANGLE{0.342020} = 20; 
	$ANGLE{0.358368} = 21; 
	$ANGLE{0.374607} = 22; 
	$ANGLE{0.390731} = 23; 
	$ANGLE{0.406737} = 24; 
	$ANGLE{0.422618} = 25; 
	$ANGLE{0.438371} = 26; 
	$ANGLE{0.453990} = 27; 
	$ANGLE{0.469472} = 28; 
	$ANGLE{0.484810} = 29; 
	$ANGLE{0.500000} = 30; 
	$ANGLE{0.515038} = 31; 
	$ANGLE{0.529919} = 32; 
	$ANGLE{0.544639} = 33; 
	$ANGLE{0.559193} = 34; 
	$ANGLE{0.573576} = 35; 
	$ANGLE{0.587785} = 36; 
	$ANGLE{0.601815} = 37; 
	$ANGLE{0.615661} = 38; 
	$ANGLE{0.629320} = 39; 
	$ANGLE{0.642788} = 40; 
	$ANGLE{0.656059} = 41; 
	$ANGLE{0.669131} = 42; 
	$ANGLE{0.681998} = 43; 
	$ANGLE{0.694658} = 44; 
	$ANGLE{0.707107} = 45; 
	$ANGLE{0.719340} = 46; 
	$ANGLE{0.731354} = 47; 
	$ANGLE{0.743145} = 48; 
	$ANGLE{0.754710} = 49; 
	$ANGLE{0.766044} = 50; 
	$ANGLE{0.777146} = 51; 
	$ANGLE{0.788011} = 52; 
	$ANGLE{0.798636} = 53; 
	$ANGLE{0.809017} = 54; 
	$ANGLE{0.819152} = 55; 
	$ANGLE{0.829038} = 56; 
	$ANGLE{0.838671} = 57; 
	$ANGLE{0.848048} = 58; 
	$ANGLE{0.857167} = 59; 
	$ANGLE{0.866025} = 60; 
	$ANGLE{0.874620} = 61; 
	$ANGLE{0.882948} = 62; 
	$ANGLE{0.891007} = 63; 
	$ANGLE{0.898794} = 64; 
	$ANGLE{0.906308} = 65; 
	$ANGLE{0.913545} = 66; 
	$ANGLE{0.920505} = 67; 
	$ANGLE{0.927184} = 68; 
	$ANGLE{0.933580} = 69; 
	$ANGLE{0.939693} = 70; 
	$ANGLE{0.945519} = 71; 
	$ANGLE{0.951057} = 72; 
	$ANGLE{0.956305} = 73; 
	$ANGLE{0.961262} = 74; 
	$ANGLE{0.965926} = 75; 
	$ANGLE{0.970296} = 76; 
	$ANGLE{0.974370} = 77; 
	$ANGLE{0.978148} = 78; 
	$ANGLE{0.981627} = 79; 
	$ANGLE{0.984808} = 80; 
	$ANGLE{0.987688} = 81; 
	$ANGLE{0.990268} = 82; 
	$ANGLE{0.992546} = 83; 
	$ANGLE{0.994522} = 84; 
	$ANGLE{0.996195} = 85; 
	$ANGLE{0.997564} = 86; 
	$ANGLE{0.998630} = 87; 
	$ANGLE{0.999391} = 88; 
	$ANGLE{0.999848} = 89; 
	$ANGLE{1.000000} = 90; 
}


sub Log() {
return;
	my $DATE=`date "+%Y-%m-%d %H:%M"`;
	chomp($DATE);
	
	open(LOG, ">>$LOG");# || warn "Couldn't update log file ($LOG) [$!]\n";
	print LOG "$DATE|$ENV{'REMOTE_ADDR'}|@_\n";
	close(LOG);	
}

