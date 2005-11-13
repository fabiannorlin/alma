#!/opt/python/bin/python
# -*- coding: iso-8859-1 -*-
# $Id: alma.cgi,v 1.7 2005/11/13 17:19:46 kent Exp $
# Svenska almanackan
# Copyright 2004 Kent Engstr�m. Released under GPL.

import time
import cgi
import cgitb; cgitb.enable()

import alma

# Auxiliary routines
def guarded_int(s, min = None, max = None):
    try:
	n = int(s)
	if min is not None and n < min: return None
	if max is not None and n > max: return None
	return n
    except TypeError:
	return None

def selected(bool):
    if bool:
	return "SELECTED"
    else:
	return ""
#
# CGI driver
#

def handle_cgi():
    form = cgi.FieldStorage()

    # �r det h�r en beg�ran om vCalendar-data, som hanteras separat?
    if form.getfirst("vcal_preview") is not None or form.getfirst("vcal_generate") is not None:
	return handle_vcal(form)

    # N�h�, d� kan vi utg� fr�n att det blir en vanlig webbsida...
    so = sys.stdout
    so.write("Content-Type: text/html\r\n\r\n")

    # Ta reda p� �r och m�nad
    year_string = form.getfirst("year")
    month_string = form.getfirst("month")

    # Om b�de �r och m�nad saknas: l�t det bli innevarande m�nad
    if year_string is None and month_string is None:
	year_string = str(time.localtime().tm_year)
	month_string = str(time.localtime().tm_mon)

    # Omvandla till heltal och kolla gr�nser
    year = guarded_int(year_string, min=1754)
    month = guarded_int(month_string, min=1, max=12)

    # Om anv�ndaren valt f.g. eller n�sta m�nad: justera
    if form.getfirst("prev") is not None:
	year, month = alma.previous_month(year, month)
    elif form.getfirst("next") is not None:
	year, month = alma.next_month(year, month)

    # Kalendertyp
    calendar_type = form.getfirst("type","vertical")
    if not calendar_type in ["vertical", "tabular"]:
	calendar_type = None

    # Utskriftsformat?
    print_format = form.getfirst("print") is not None

    # Ta hand om uppenbara fel
    if year is None or month is None or calendar_type is None:
	so.write("<P>Fel p� anrop till almanacksprogrammet!\n")
	return

    # Generera almanackan
    yc = alma.YearCal(year)
    mc = alma.MonthCal(yc, month)

    # Visa huvud
    head = '%s %s' % (mc.month_name, year)
    so.write('<HEAD>')
    so.write('<TITLE>%s</TITLE>' % head)
    so.write('<LINK TYPE="text/css" REL="stylesheet" HREF="alma.css">')
    so.write('</HEAD>\n')
    
    so.write('<BODY>')

    # Navigering
    if not print_format:
        so.write('<FORM METHOD=POST>')

        # M�nad
        so.write('<SELECT NAME="month" onChange="this.form.submit();">')
        for m in range(1,13):
	    so.write('<OPTION VALUE="%d" %s>%s</OPTION>' % (m, selected(m == month), alma.month_names[m]))
        so.write('</SELECT>\n')

        # �r
        so.write('<INPUT TYPE=INPUT NAME="year" VALUE="%d" SIZE="4" onChange="this.form.submit();">\n' % (year))

        # Typ
        so.write('<SELECT NAME="type" onChange="this.form.submit();">')
        for (value, label) in (("vertical", "Vertikal"),
			       ("tabular",  "Tabell")):
	    so.write('<OPTION VALUE="%s" %s>%s</OPTION>' % (value, selected(calendar_type == value), label))
        so.write('</SELECT>\n')

        # Uppdatera
        so.write('<INPUT TYPE=SUBMIT NAME="go" VALUE="Uppdatera">\n')

        # Utskrift (= ingen navigering)
        so.write('<INPUT TYPE=SUBMIT NAME="print" VALUE="Visa f�r utskrift">\n')

        # vCalendar
        so.write('<INPUT TYPE=SUBMIT NAME="vcal_preview" VALUE="vCalendar">\n')

        so.write(" ~ ")

        # Snabbl�nkar till f�reg�ende och n�sta m�nad
        py, pm = alma.previous_month(year, month)
        ny, nm = alma.next_month(year, month)
        so.write('<INPUT TYPE=SUBMIT NAME="prev" VALUE="F�reg�ende m�nad">\n')
        so.write('<INPUT TYPE=SUBMIT NAME="next" VALUE="N�sta m�nad">\n')


        so.write('</FORM>')
    
    # Rubrik
    if calendar_type == "vertical":
	so.write('<H1>%s</H1>\n' % head)
    else:
	so.write('<H1 CLASS="centered">%s</H1>\n' % head)

    # Visa almanackan
    if calendar_type == "vertical":
	mc.html_vertical(sys.stdout)
    elif calendar_type == "tabular":
	mc.html_tabular(sys.stdout)

    # Disclaimer
    if not print_format:
	so.write('''<DIV CLASS="disclaimer">Vi kan inte l�mna n�gra garantier
f�r att almanackan �r fullst�ndig och korrekt. Fr�n och med 1983 b�r det
emellertid inte finnas n�gra st�rre felaktigheter.
Vi f�rs�ker att g�ra s� gott vi kan och tar tacksamt emot synpunkter till
<A HREF="mailto:kent@lysator.liu.se">kent@lysator.liu.se</A>.
</DIV>''')
	
    # Slut
    so.write('</BODY>')


def handle_vcal(form):
    so = sys.stdout

    # Ta reda p� �r
    year_string = form.getfirst("year")
    if year_string is None:
	year_string = str(time.localtime().tm_year)
    year = guarded_int(year_string, min=1754)

    # F�rhandsvisning eller generering?
    preview = form.getfirst("vcal_preview")

    if preview:
	so.write('Content-Type: text/html\r\n')
    else:
	so.write('Content-Type: text/x-vCalendar\r\n')
	so.write('Content-disposition: attachment; filename=%d.ics\r\n' % year)
	
    so.write('\r\n')

    # Generera almanackan
    yc = alma.YearCal(year)

    # Huvud med val av vad som ska visas
    if preview:
	so.write('<HEAD><TITLE>%d</TITLE></HEAD>\n' % year)
	so.write('<BODY><H1>vCalendar-fil f�r �r %d</H1>\n' % year)

	so.write('<P>V�lj nedan vilken information som ska med i vCalendar-filen. ')
	so.write('Beg�r sedan en ny f�rhandsvisning eller tryck direkt p� knappen ')
	so.write('f�r att ladda ner vCalendar-filen. ')

	so.write('<FORM><UL>\n')

    # Val av vad som ska visas
    pdict = {}
    nodefaults = form.getfirst("vcal_nodefaults")
    for (param, default, text) in [(str(alma.MRED),   True,  "Visa viktiga r�da dagar"),
				   (str(alma.RED),    False, "Visa mindre viktiga r�da dagar"),
				   (str(alma.MBLACK), True,  "Visa viktiga svarta dagar"),
				   (str(alma.BLACK),  False, "Visa mindre viktiga svarta dagar"),
				   ("red",            False, "Markera r�da dagar"),
				   ("names",          False, "Visa namnsdagsnamn"),
				   ("moon",           False, "Visa m�nfaser"),
				   ("flag",           False, "Visa flaggdagar"),
				   ]:
	# Ta hand om inskickat v�rde
	if nodefaults:
	    value = form.getfirst("vcal_" + param)
	    if value == "yes":
		pdict[param] = True
	    else:
		pdict[param] = False
	else:
	    pdict[param] = default
    
	# Erbjud uppdatering
	if preview:
	    if pdict[param]:
		checked = " CHECKED"
	    else:
		checked = ""
		
	    so.write('<LI><INPUT TYPE="CHECKBOX" NAME="vcal_%s" VALUE="yes" %s> %s\n' % (param, checked, text))

    # Slut p� huvud
    if preview:
	so.write('</UL>\n')
	so.write('<INPUT TYPE="HIDDEN" NAME="year" VALUE="%d">\n' % year)
	so.write('<INPUT TYPE="HIDDEN" NAME="vcal_nodefaults" VALUE="yes">\n')
	so.write('<INPUT TYPE="SUBMIT" NAME="vcal_preview" VALUE="Uppdatera f�rhandsvisning">\n')
	so.write('<INPUT TYPE="SUBMIT" NAME="vcal_generate" VALUE="Ladda ner vCalendar-fil">\n')
	so.write('</FORM>\n')

    # Kalender (f�rhandsvisning eller p� riktigt)
    if preview:
	so.write('<P>F�rhandsvisning av information som exporteras till vCalendar-filen:\n')
	so.write('<PRE>\n')
    else:
	so.write('BEGIN:VCALENDAR\n')
	so.write('VERSION:1.0\n')
	so.write('PRODID:alma.cgi\n')
	
    for dc in yc.generate():
	ymd = "%04d-%02d-%02d" % (dc.y, dc.m, dc.d)
	dtstart = "%04d%02d%02dT000000" % (dc.y, dc.m, dc.d)

	show = False
	parts = []

	# R�da och svarta dagar
	for dayclass in range(alma.MRED, alma.BLACK+1):
	    if pdict[str(dayclass)]:
		for dayname in dc.day_names:
		    if dayname.dayclass == dayclass:
			name = dayname.name
			if pdict["red"] and dayname.is_red:
			    name = name + " (r�d)"
			parts.append(name)

	# Namnsdagar
	if pdict["names"]:
	    parts.extend(dc.names)

	# M�nfaser
	if pdict["moon"]:
	    phase = dc.moonphase_name()
	    if phase:
		parts.append(phase)

	# M�nfaser
	if pdict["flag"]:
	    if dc.flag_day:
		parts.append("flaggdag")
	
	# Visa dagen?
	if parts:
	    text = ", ".join(parts)
	    if preview:
		so.write("%-10s %s\n" % (ymd, text))
	    else:
		so.write('BEGIN:VEVENT\n')
		so.write('SUMMARY;CHARSET=ISO-8859-1:%s\n' % text)
		so.write('DTSTART:%s\n' % dtstart)
		so.write('END:VEVENT\n')


    # Slut p� kalendern
    if preview:
	so.write('</PRE>\n')
    else:
	so.write('END:VCALENDAR\n')

    # Slut p� sidan
    if preview:
	so.write('</BODY>\n')


#
# Invocation
#

if __name__ == '__main__':
    import sys
    handle_cgi()
