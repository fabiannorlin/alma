#!/opt/python/bin/python
# -*- coding: iso-8859-1 -*-
# $Id: alma.cgi,v 1.2 2004/12/27 20:21:37 kent Exp $
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
    so = sys.stdout
    so.write("Content-Type: text/html\r\n\r\n")

    form = cgi.FieldStorage()

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
        so.write('<SELECT NAME="month">')
        for m in range(1,13):
	    so.write('<OPTION VALUE="%d" %s>%s</OPTION>' % (m, selected(m == month), alma.month_names[m]))
        so.write('</SELECT>\n')

        # �r
        so.write('<INPUT TYPE=INPUT NAME="year" VALUE="%d" SIZE="4">\n' % (year))

        # Typ
        so.write('<SELECT NAME="type">')
        for (value, label) in (("vertical", "Vertikal"),
    			   ("tabular",  "Tabell")):
	    so.write('<OPTION VALUE="%s" %s>%s</OPTION>' % (value, selected(calendar_type == value), label))
        so.write('</SELECT>\n')


        # Uppdatera
        so.write('<INPUT TYPE=SUBMIT NAME="go" VALUE="Uppdatera">\n')

        # Utskrift (= ingen navigering)
        so.write('<INPUT TYPE=SUBMIT NAME="print" VALUE="Utskriftsformat">\n')

        so.write(" ~ ")

        # Snabbl�nkar till f�reg�ende och n�sta m�nad
        py, pm = alma.previous_month(year, month)
        ny, nm = alma.next_month(year, month)
        so.write('<INPUT TYPE=SUBMIT NAME="prev" VALUE="F�reg�ende m�nad">\n')
        so.write('<INPUT TYPE=SUBMIT NAME="next" VALUE="N�sta m�nad">\n')


        so.write('</FORM>')
    
    # Rubrik
    so.write('<H1>%s</H1>\n' % head)

    # Visa almanackan
    if calendar_type == "vertical":
	mc.html_vertical(sys.stdout)
    else:
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


#
# Invocation
#

if __name__ == '__main__':
    import sys
    handle_cgi()
