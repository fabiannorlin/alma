#!/opt/python/bin/python
# -*- coding: iso-8859-1 -*-
# $Id: alma.py,v 1.4 2004/12/08 19:44:51 kent Exp $
# Svenska almanackan
# Copyright 2004 Kent Engstr�m. Released under GPL.

import time
import math
from cStringIO import StringIO

import jddate; JD=jddate.FromYMD


#
# Data
#

# M�nader (index 1..12)
month_names =   [None,
		 "Januari", "Februari", "Mars",
		 "April", "Maj", "Juni",
		 "Juli", "Augusti", "September",
		 "Oktober", "November", "December"]

# Veckodagar (index 1..7)
wday_names = [None, "M�ndag", "Tisdag", "Onsdag",
	      "Torsdag", "Fredag", "L�rdag", "S�ndag"]

# Tidszon (positivt �t �ster)
TIMEZONE = 1

#
# Funktioner
#

# Ber�kna vilken dag som �r p�sks�ndag ett visst �r 
# Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 31

def easter_sunday(year):
    a = year % 19
    b , c = divmod(year, 100)
    d , e = divmod(b, 4)
    f = (b+8) / 25
    g = (b-f+1) / 3
    h = (19*a+b-d-g+15) % 30
    i, k = divmod(c, 4)
    l = (32+2*e+2*i-h-k) % 7
    m = (a+11*h+22*l) / 451
    n, p = divmod(h+l-7*m+114, 31)

    return JD(year, n, p+1)

# Ber�kna JD d� en viss m�nfas intr�ffar i en viss cykel
# Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 159


def moonphase(cycle, phase):
    # Ber�kna parametrar
    # phase: 0 �r nym�ne, 1 �r v�xande halvm�ne, 2 �r fullm�ne, 3 �r avtagande halvm�ne
    assert phase in [0,1,2,3]
    k = cycle + phase/4.0
    t  = k / 1236.85

    # Ber�kna ursprunglig "gissning"

    jd = 2415020.75933 \
	+ 29.53058868 * k \
	+ 0.0001178 * t*t \
	- 0.000000155 * t*t*t \
	+ 0.00033 * math.sin(2.90702 + 2.31902 * t + 0.0001601 * t*t)

    # Ber�kna positioner vid denna tidpunkt

    m  = 359.2242 +  29.10535608 * k - 0.0000333 * t*t - 0.00000347 * t*t*t
    mp = 306.0253 + 385.81691806 * k + 0.0107306 * t*t + 0.00001236 * t*t*t
    f  =  21.2964 + 390.67050646 * k - 0.0016528 * t*t - 0.00000239 * t*t*t
    m  *=  math.pi/180.0
    mp *=  math.pi/180.0
    f  *=  math.pi/180.0

    # Korrigera "gissningen" m a p dessa positioner

    if phase in [0, 2]: 
	# Nym�ne och fullm�ne
	jd += (0.1734 - 0.000393*t) * math.sin(m) \
	    + 0.0021 * math.sin(2*m) \
	    - 0.4068 * math.sin(mp) \
	    + 0.0161 * math.sin(2*mp) \
	    - 0.0004 * math.sin(3*mp) \
	    + 0.0104 * math.sin(2*f) \
	    - 0.0051 * math.sin(m+mp) \
	    - 0.0074 * math.sin(m-mp) \
	    + 0.0004 * math.sin(2*f+m) \
	    - 0.0004 * math.sin(2*f-m) \
	    - 0.0006 * math.sin(2*f+mp) \
	    + 0.0010 * math.sin(2*f-mp) \
	    + 0.0005 * math.sin(m+2*mp)
    else:
	# V�xande och avtagande halvm�ne
	  jd += (0.1721 - 0.0004*t) * math.sin(m) \
	      + 0.0021 * math.sin(2*m) \
	      - 0.6280 * math.sin(mp) \
	      + 0.0089 * math.sin(2*mp) \
	      - 0.0004 * math.sin(3*mp) \
	      + 0.0079 * math.sin(2*f) \
	      - 0.0119 * math.sin(m+mp) \
	      - 0.0047 * math.sin(m-mp) \
	      + 0.0003 * math.sin(2*f+m) \
	      - 0.0004 * math.sin(2*f-m) \
	      - 0.0006 * math.sin(2*f+mp) \
	      + 0.0021 * math.sin(2*f-mp) \
	      + 0.0003 * math.sin(m+2*mp) \
	      + 0.0004 * math.sin(m-2*mp) \
	      - 0.0003 * math.sin(2*m+mp)

	  if phase == 1:
	      jd += 0.0028 - 0.0004*math.cos(m) + 0.0003*math.cos(mp);
	  else:
	      jd -= (0.0028 - 0.0004*math.cos(m) + 0.0003*math.cos(mp));

    # Korrigera f�r:
    # 1) Resten av programmet har en lite annorlunda definition av JD.
    #    JD h�r = JD i resten - 0.5 dygn
    #  2) Tidszon

    jd = jd + 0.5 + TIMEZONE/24.0

    # Dela upp i dag, timme, minut

    day  = int(jd)
    rest = (jd - day) * 24
    hour = int(rest)
    min  = int((rest - hour) * 60);

    # �terv�nd med datumtyp, kasta tillsvidare h och m
    return jddate.FromJD(day)


# F�rsta veckodagen av visst slag p� eller efter ett visst datum
def first_weekday(y, m, d, wd):
    jd = JD(y, m, d)
    (_, _, jdwd) = jd.GetYWD()
    diff = wd - jdwd
    if diff < 0: diff = diff + 7
    return jd + diff

def first_sunday(y, m, d):
    return first_weekday(y, m, d, 7)

def first_saturday(y, m, d):
    return first_weekday(y, m, d, 6)

#
# Klasser
#

class DayCal:
    """Class to represent a single day."""
    def __init__(self, jd):
	self.jd = jd           # jddate

	(self.y,
	 self.m,
	 self.d) = self.jd.GetYMD()

	(self.wyear,
	 self.week,
	 self.wday) = self.jd.GetYWD()

	self.flag_day = False  # flaggdag?
	self.red_names = []    # heldagsnamn
	self.black_names = []  # andra namn (som ej g�r dagen r�d)
	self.names = []        # namnsdagsnamn
	self.wday_name = wday_names[self.wday]
	self.wday_name_short = self.wday_name[:3]

	if self.wday == 7:
	    self.red = True    # Alla s�ndagar �r r�da
	else:
	    self.red = False   # Alla andra dagar �r svarta tillsvidare

	self.moonphase = None  # M�nfas (0 = nym�ne, 1, 2 = fullm�ne, 3)
 
    def add_info(self, red, flag, name):
	if red:
	    self.red = True
	    if name: self.red_names.append(name)
	else:
	    if name: self.black_names.append(name)
	
	if flag:
	    self.flag_day = True
    
    def set_names(self, names):
	self.names = names

    def set_moonphase(self, moonphase):
	self.moonphase = moonphase

    def __repr__(self):
	return "<Day %s>"  % self.jd.GetString_YYYY_MM_DD()

    def html_vertical(self, f):
	if self.red:
	    colour = "red"
	else:
	    colour = "black"

	f.write('<TR CLASS="v">')

	# Veckonr �verst och varje m�ndag
	if self.d == 1 or self.wday == 1:
	    f.write('<TD CLASS="vweek_present">%d</TD>' % (self.week))
	else:
	    f.write('<TD CLASS="vweek_empty">&nbsp;</TD>')

	# Veckodagens tre f�rst tecken
	f.write('<TD CLASS="vwday_%s">%s</TD>' % (colour, self.wday_name_short))

	# Dagens nummer
	f.write('<TD CLASS="vday_%s">%d</TD>' % (colour, self.d))

	# Flaggdagar och m�nfaser
	f.write('<TD CLASS="vflag">')
	empty = True

	if self.flag_day:
	    f.write('<IMG SRC="flag.gif">')
	    empty = False

	if self.moonphase is not None:
	    f.write('<IMG SRC="moonphase%d.gif">' % self.moonphase)
	    empty = False

	if empty:
	    f.write('&nbsp;')
	f.write('</TD>')

	# Dagens namn. �verst r�da, svarta. Under namnsdagar
	redblack = []
	for name in self.red_names:
	    redblack.append('<SPAN CLASS="vname_red">%s</SPAN>' % name)
	for name in self.black_names:
	    redblack.append('<SPAN CLASS="vname_black">%s</SPAN>' % name)
	redblack_string = ", ".join(redblack)
	name_string = ", ".join(self.names)
	
	f.write('<TD CLASS="vnames">')
	f.write(redblack_string)
	if redblack_string and name_string: f.write('<BR>')
	f.write(name_string)
	f.write('&nbsp;</TD>')

	f.write('</TR>\n')

    def dump(self):
	"""Show in text format for debugging."""
	print "%s %3s %2d %s%s %s %s %s" % (self.jd.GetString_YYYY_MM_DD(),
					    self.wday_name_short,
					    self.week,
					    " *"[self.red],
					    " F"[self.flag_day],
					    self.red_names,
					    self.black_names,
					    self.names,
					    )

class YearCal:
    """Class to represent a whole year."""

    def __init__(self, year):
	self.year = year       # �r (exv. 2004)
	self.jd_jan1 = JD(year, 1, 1)
	self.jd_dec31 = JD(year, 12, 31)

	# Skapa alla dagar f�r �ret
	self.days = []
	jd = self.jd_jan1
	while jd <= self.jd_dec31:
	    self.days.append(DayCal(jd))
	    jd = jd + 1

	# Skott�r?
	if len(self.days) == 365:
	    self.leap_year = False
	elif len(self.days) == 366:
	    self.leap_year = True
	else:
	    assert ValueError, "bad number of days in a year"

	# Helgdagar, flaggdagar med mera
	self.place_names()

	# Namnsdagar
	if year >= 2001:
	    self.place_name_day_names("namnsdagar-2001.txt")
	elif year >= 1993:
	    self.place_name_day_names("namnsdagar-1993.txt")
	elif year >= 1986:
	    self.place_name_day_names("namnsdagar-1986.txt")
	elif year >= 1901:
	    self.place_name_day_names("namnsdagar-1901.txt",
				      [(1905, 11,  4, ["Sverker"]),
				       (1907, 11, 27, ["Astrid"]),
				       (1934, 10, 20, ["Sibylla"])])

	# M�nfaser
	self.place_moonphases()

    # H�mta dag givet m, d
    def get_md(self, m, d):
	jd = JD(self.year, m, d)
	return self.days[jd - self.jd_jan1]

    # H�mta dag givet jd
    def get_jd(self, jd):
	(y, m, d) = jd.GetYMD()
	assert y == self.year
	return self.days[jd - self.jd_jan1]

    # L�gg till information f�r m, d
    def add_info_md(self, m, d, red, flag, name):
	dc = self.get_md(m, d)
	dc.add_info(red, flag, name)

    # L�gg till information f�r jd
    def add_info_jd(self, jd, red, flag, name):
	dc = self.get_jd(jd)
	dc.add_info(red, flag, name)

    def place_names(self):
	"""Place holidays etc. in the calendar."""

	# Fasta helgdagar och flaggdagar

	for (from_year, to_year, m, d, red, flag, name) in \
	    [(None, None,  1,  1, True , True,  "Ny�rsdagen"),
	     (None, None,  1, 28, False, True,  None), # Konungens namnsdag
	     (None, None,  1,  5, False, False, "Trettondedagsafton"),
	     (None, None,  1,  6, True,  False, "Trettondedag jul"),
	     (None, None,  1, 13, False, False, "Tjugondedag Knut"),
	     (None, None,  3, 12, False, True,  None), # Kronprinsessans namnsdag
	     (None, None,  4, 30, False, True,  "Valborgsm�ssoafton"), # + Konungens f�delsedag
	     (None, None,  5,  1, True,  True,  "F�rsta maj"),
	     (None, 2004,  6,  6, False, True,  "Sveriges nationaldag"),
	     (2005, None,  6,  6, True, True,  "Sveriges nationaldag"),
	     (None, None,  7, 14, False, True,  None), # Kronprinsessans f�delsedag
	     (None, None,  8,  8, False, True,  None), # Drottningens namnsdag
	     (None, None, 10, 24, False, True,  "FN-dagen"),
	     (None, None, 11,  6, False, True,  None), # Gustav Adolfsdagen
	     (None, None, 12, 10, False, True,  "Nobeldagen"),
	     (None, None, 12, 23, False, True,  None), # Drottningens f�delsedag
	     (None, None, 12, 24, False, False, "Julafton"),
	     (None, None, 12, 25, True,  True,  "Juldagen"),
	     (None, None, 12, 26, True,  False, "Annandag jul"),
	     (None, None, 12, 28, False, False, "Menl�sa barns dag"),
	     (None, None, 12, 31, False, False, "Ny�rsafton"),
	     ]:
	    if from_year is not None and self.year < from_year: continue
	    if to_year is not None and self.year > to_year: continue
	    self.add_info_md(m, d, red, flag, name)

	# Skottdagen inf�ll den 24/2 -1996, infaller den 29/2 2000-
	if self.leap_year:
	    if self.year >= 2000:
		self.add_info_md(2, 29, False, False, "Skottdagen")
	    else:
		self.add_info_md(2, 24, False, False, "Skottdagen")

	# P�sks�ndagen ligger till grund f�r de flesta kyrkliga helgdagarna
	# under �ret, s� den beh�ver vi r�kna ut redan h�r
	pd = easter_sunday(self.year)

	# S�ndagen efter ny�r
	sen = first_sunday(self.year, 1, 2) # F�rsta s�ndagen 2/1-
	if sen < JD(self.year, 1 ,6):  # Sl�s ut av 13dagen och 1 e 13dagen
	    self.add_info_jd(sen, True, False, "S�ndagen e ny�r")

	# Kyndelsm�ssodagen (Jungfru Marie Kyrkog�ngsdag)
	jmk = first_sunday(self.year, 2, 2)
	if jmk == pd - 49:
	    # Kyndelsm�ssodagen p� fastlagss�ndagen => Kyndelsm�ssodagen flyttas -1v
	    jmk = jmk -7
	self.add_info_jd(jmk, True, False, "Kyndelsm�ssodagen")

	# S�ndagar efter Trettondedagen
	set = first_sunday(self.year, 1, 7)
	for i in range(1,7):
	    # Sl�s ut av Kyndelsm�ssodagen och allt p�skaktigt
	    if set != jmk and set < pd-63:
		self.add_info_jd(set, True, False, "%d e trettondedagen" % i)
	    set = set + 7

	# Jungfru Marie Beb�delsedag
	if self.year < 2003: # FIXME: r�tt �r f�r byte av regel?
	    # FIXME: �r detta �ldre regel eller bara fel?
	    jmb = first_sunday(self.year, 3, 25)
	else:
	    jmb = first_sunday(self.year, 3, 22)

	# Om Jungfru Marie Beb�delsedag hamnar p� p�skdagen eller
	# palms�ndagen, s� flyttas den till s�ndagen innan
	# palms�ndagen (5 i fastan).
	if jmb >= pd - 7 and jmb <= pd:
	    jmb = pd - 14
	self.add_info_jd(jmb, True, False, "Jungfru Marie beb�delsedag")

	# Fasta, P�sk, Kristi Himmelsf�rd, Pingst

	# Dessa dagar sl�s ut av Kyndelsm�ssodagen
	for (jd, name) in [(pd-63, "Septuagesima"),
			   (pd-56, "Sexagesima")]:
	    if jd != jmk:
		self.add_info_jd(jd, True, False, name)

	# Fastlagss�ndagen och icke-helgdagar efter den
	self.add_info_jd(pd-49, True, False, "Fastlagss�ndagen")
	self.add_info_jd(pd-47, False,False, "Fettisdagen")
	self.add_info_jd(pd-46, False,False, "Askonsdagen")

	# Dessa dagar sl�s ut av Jungfru Marie beb�delsedag
	for (jd, name) in [(pd-42, "1 i fastan"),
			   (pd-35, "2 i fastan"),
			   (pd-28, "3 i fastan"),
			   (pd-21, "Midfastos�ndagen"),
			   (pd-14, "5 i fastan")]:
	    if jd != jmb:
		self.add_info_jd(jd, True, False, name)

	self.add_info_jd(pd- 7, True, False, "Palms�ndagen")
	self.add_info_jd(pd- 4, False,False, "Dymmelonsdagen")
	self.add_info_jd(pd- 3, False,False, "Sk�rtorsdagen")
	self.add_info_jd(pd- 2, True, False, "L�ngfredagen")
	self.add_info_jd(pd- 1, False,False, "P�skafton")
	self.add_info_jd(pd+ 0, True, True,  "P�skdagen")
	self.add_info_jd(pd+ 1, True, False, "Annandag p�sk")
	if self.year < 2004:
	    self.add_info_jd(pd+ 7, True, False, "1 e p�sk")
	    self.add_info_jd(pd+14, True, False, "2 e p�sk")
	    self.add_info_jd(pd+21, True, False, "3 e p�sk")
	    self.add_info_jd(pd+28, True, False, "4 e p�sk")
	else:
	    self.add_info_jd(pd+ 7, True, False, "2 i p�sktiden")
	    self.add_info_jd(pd+14, True, False, "3 i p�sktiden")
	    self.add_info_jd(pd+21, True, False, "4 i p�sktiden")
	    self.add_info_jd(pd+28, True, False, "5 i p�sktiden")
	self.add_info_jd(pd+35, True, False, "B�ns�ndagen")
	self.add_info_jd(pd+39, True, False, "Kristi himmelsf�rds dag")
	if self.year < 2004:
	    self.add_info_jd(pd+42, True, False, "6 e p�sk")
	else:
	    self.add_info_jd(pd+42, True, False, "S�ndagen f Pingst")
	self.add_info_jd(pd+48, False,False, "Pingstafton")
	self.add_info_jd(pd+49, True, True,  "Pingstdagen")
	if self.year < 2005:
	    self.add_info_jd(pd+50, True, False, "Annandag pingst")
	else:
	    self.add_info_jd(pd+50, False,False, "Annandag pingst")
	self.add_info_jd(pd+56, True,False, "Heliga trefaldighets dag")

	# Vissa dagar ska "sl� ut" vanliga "N efter trefaldighet"
	# H�ll reda p� dem i en lista i den takt de r�knas fram
	se3_stoppers = []

	# Midsommardagen
	msd = first_saturday(self.year, 6, 20)
	self.add_info_jd(msd-1, False, False, "Midsommarafton")
	self.add_info_jd(msd+0, True,  True,  "Midsommardagen")
	if self.year >= 2004:
	    self.add_info_jd(msd+1, True,  False,  "Den helige Johannes D�parens dag")
	    se3_stoppers.append(msd+1)

	# Alla Helgons dag
	ahd = first_saturday(self.year, 10, 31)
	self.add_info_jd(ahd+0, True, False, "Alla helgons dag")
	self.add_info_jd(ahd+1, True, False, "S�ndagen e alla helgons dag")
	se3_stoppers.append(ahd+1)

	# Advent (samt Doms�ndagen och S�ndagen f�re doms�ndagen)
	adv1=first_sunday(self.year, 11, 27 )
	self.add_info_jd(adv1-14, True, False, "S�ndagen f doms�ndagen")
	self.add_info_jd(adv1- 7, True, False, "Doms�ndagen")
	self.add_info_jd(adv1+ 0, True, False, "1 i Advent")
	self.add_info_jd(adv1+ 7, True, False, "2 i Advent")
	self.add_info_jd(adv1+14, True, False, "3 i Advent")
	self.add_info_jd(adv1+21, True, False, "4 i Advent")

	# Den helige Mikaels dag, s�ndag i tiden 29/9 till 5/10
	hmd = first_sunday(self.year, 9, 29)
	self.add_info_jd(hmd, True, False, "Den helige Mikaels dag")
	se3_stoppers.append(hmd)

	# Tacks�gelsedagen, andra s�ndagen i oktober
	tsd = first_sunday(self.year, 10, 8)
	self.add_info_jd(tsd, True, False, "Tacks�gelsedagen")
	se3_stoppers.append(tsd)

	# S�ndagarna efter Trefaldighet
	se3 = pd+63
	for i in range(1,28):
	    # Ska dagen vara en S e Tr?
	    if se3 >= adv1 - 14:
		# Inte l�nt l�ngre efter S f ds
		break
	    
	    # Har dagen redan ett annat namn som har prioritet?
	    if se3 in se3_stoppers:
		se3 += 7
		continue

	    # S�rskilda namn f�r vissa av dagarna
	    if i == 5:
		name = "Apostladagen"
	    elif i == 7:
		name = "Kristi f�rklarings dag"
	    else:
		name = "%d e trefaldighet" % i
	    
	    self.add_info_jd(se3, True, False, name)
	    se3 += 7

    def place_name_day_names(self, filename, patches = None):
	for line in open(filename):
	    (ms, ds, ns) = line.strip().split(None,2)
	    m = int(ms)
	    d = int(ds)
	    # Innan �r 2000, d� skottdagen var 24/2, s� flyttades
	    # namnen till senare dagar i februari
	    if self.leap_year and self.year < 2000 and m == 2 and d >= 24: 
		d = d + 1
	    names = ns.split(",")
	    dc = self.get_md(m, d)
	    dc.set_names(names)
	if patches is not None:
	    for (from_year, m, d, names) in patches:
		if self.year >= from_year:
		    dc = self.get_md(m, d)
		    dc.set_names(names)
		    

    # Placera ut m�nfaserna i almanackan.
    # Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 159
    def place_moonphases(self):
	# FIXME:
	# int midcycle,cycle;
	# moon_t phase;
	# int h,m;
	# day_cal *dcal;
	# jd_t jd1jan,jd31dec,jd;

	# Ta reda p� en m�ncykel i mitten av �ret (ungef�r)
	midcycle = int((self.year - 1900) * 12.3685) + 6

	# Arbeta bak�t mot b�rjan av �ret och placera ut m�nfaserna

	cycle = midcycle
	phase = 0 # Nym�ne

	while True:
	    jd = moonphase(cycle, phase)
	    if jd < self.jd_jan1: break
	    
	    dc = self.get_jd(jd)
	    dc.set_moonphase(phase)

	    if phase == 0:
		phase = 3
		cycle = cycle - 1
	    else:
		phase = phase -1 

	# Arbeta fram�t mot slutet av �ret och placera ut m�nfaserna

	cycle = midcycle
	phase = 0 # Nym�ne

	while True:
	    jd = moonphase(cycle, phase)
	    if  jd > self.jd_dec31: break

	    dc = self.get_jd(jd)
	    dc.set_moonphase(phase)

	    if phase == 3:
		phase = 0
		cycle = cycle + 1
	    else:
		phase = phase + 1 

    def dump(self):
	"""Show in text format for debugging."""

	for m in range(1,13):
	    mc = MonthCal(self, m)
	    mc.dump()
	
class MonthCal:
    """Class to represent a month of a year."""

    def __init__(self, yearcal, month):
	self.yc = yearcal
	assert 1<= month <= 12
	self.month = month
	self.month_name = month_names[self.month]

	self.num_days = [None, 31, 28, 31, 30, 31, 30,
			 31, 31, 30, 31, 30, 31][self.month]
	if self.yc.leap_year and self.month == 2:
	     self.num_days = 29

    def generate(self):
	for d in range(1,self.num_days+1):
	    dc = self.yc.get_md(self.month, d)
	    yield dc

    def html_vertical(self, f):
	head = '%s %s' % (self.month_name, self.yc.year)

	f.write('<HEAD>')
	f.write('<TITLE>%s</TITLE>' % head)
	f.write('<LINK TYPE="text/css" REL="stylesheet" HREF="alma.css">')
	f.write('</HEAD>\n')

	f.write('<BODY>')
	f.write('<H1>%s</H1>\n' % head)

	# L�nkar bak�t och fram�t
	if self.month == 1:
	    pm = 12
	    py = self.yc.year - 1
	else:
	    pm = self.month - 1
	    py = self.yc.year

	if self.month == 12:
	    nm = 1
	    ny = self.yc.year +1
	else:
	    nm = self.month + 1
	    ny = self.yc.year

	f.write('<P>')
	f.write('<A HREF="?year=%d&month=%d">[%s %d]</A>' % (py, pm,
							   month_names[pm], py))
	f.write(' ~ ')
	f.write('<A HREF="?year=%d&month=%d">[%s %d]</A>' % (ny, nm,
							   month_names[nm], ny))
	f.write('</P>')

	# Tabellen med dagarna
	f.write('<TABLE CLASS="vtable">')
	for dc in self.generate():
	    dc.html_vertical(f)
	f.write('<TR CLASS="v"><TD CLASS="vlast" COLSPAN="5">&nbsp;</TD></TR>')
	f.write('</TABLE>')
	f.write('</BODY>')

    def dump(self):
	"""Show in text format for debugging."""
	print self.month_name
	print
	for dc in self.generate():
	    dc.dump()
	print

#
# CGI driver
#

def handle_cgi():
    print "Content-Type: text/html\r\n\r"

    import cgi
    import cgitb; cgitb.enable()
    form = cgi.FieldStorage()

    year_string = form.getfirst("year")
    month_string = form.getfirst("month")
    if year_string is None and month_string is None:
	year_string = str(time.localtime().tm_year)
	month_string = str(time.localtime().tm_mon)

    try:
	year = int(year_string)
    except TypeError:
	year = None

    try:
	month = int(month_string)
	if month < 1: month = 1
	if month > 12: month = 12
    except TypeError:
	month = None

    if year is not None and month is not None:
	yc = YearCal(year)
	mc = MonthCal(yc, month)
	mc.html_vertical(sys.stdout)
    else:
	print "<P>Fel"


#
# Invocation
#

if __name__ == '__main__':
    import sys
    handle_cgi()

    #yc = YearCal(int(sys.argv[1]))
    #yc.dump()
