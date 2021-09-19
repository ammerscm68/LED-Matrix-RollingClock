#!/usr/bin/env python
# -- coding: utf-8 --
#--------------------------------------------------------------------------
#Mit diesem Script können die Feiertage in Deutschland berechnet und
#ausgegeben werden. Wird dem Script ein Bundesland übergeben, werden alle
#Feiertage dieses Bundeslandes ausgegeben. Wird kein Bundesland übergeben,
#so werden nur die bundeseinheitlichen Feiertage ausgegeben.
#Autor: Stephan John
#Version: 1.1
#Datum: 25.05.2012
#Danke an Paul Wachendorf für die Hinweise
#2016 erweitert für smarthomeNG.py fpr D/CH/A von Manuel Holländer (Bonze255/Fragger255)
#-----------------------------------------------------------------------------#
#

import datetime
import pprint
state_codes = {
            #"""Bundesländer Deutschland"""
            'Baden-Württemberg':'BW',
            'Bayern':'BY',
            'Berlin':'BE',
            'Brandenburg':'BB',
            'Bremen':'HB',
            'Hamburg':'HH',
            'Hessen':'HE',
            'Mecklenburg-Vorpommern':'MV',
            'Niedersachsen':'NI',
            'Nordrhein-Westfalen':'NW',
            'Rheinland-Pfalz':'RP',
            'Saarland':'SL',
            'Sachsen':'SN',
            'Sachsen-Anhalt':'SA',
            'Schleswig-Holstein':'SH',
            'Thüringen':'TH',

            #"""Bundesländer Oesterreich"""
            'Burgenland':'B',
            'Kärnten':'K',
            'Niederösterreich':'N',
            'Oberösterreich':'O',
            'Land Salzburg':'S',
            'Steiermark':'ST',
            'Tirol':'T',
            'Vorarlberg':'V',
            'Wien':'W',

            #"""Kantone Schweiz"""
            'Kanton Zürich':'KZH',
            'Kanton Bern':'KBE',
            'Kanton Luzern':'KLU',
            'Kanton Uri':'KUR',
            'Kanton Schwyz':'KSZ',
            'Kanton Obwalden':'KOW',
            'Kanton Nidwalden':'KNW',
            'Kanton Glaraus':'KGL',
            'Kanton Zug':'KZG',
            'Kanton Freiburg':'KFR',
            'Kanton Solothurn':'KSO',
            'Kanton Basel Stadt':'KBS',
            'Kanton Basel Landschaft':'KBL',
            'Kanton Schaffhausen':'KSH',
            'Kanton Appenzell Ausserhoden':'KAR',
            'Kanton Appenzell Innerhoden':'KAL',
            'Kanton St.Gallen':'KSG',
            'Kanton Graubünden':'KGR',
            'Kanton Aargau':'KAG',
            'Kanton Thurgau':'KTG',
            'Kanton Tessin':'KTI',
            'Kanton Waadt':'KVD',
            'Kanton Wallis':'KVS',
            'Kanton Neuenburg':'KNE',
            'Kanton Genf':'KGE',
            'Kanton Jura':'KJU',
           }

def holidays(year, state=None):
    """
    prüft die eingegebenen Werte für die Berechnung der Feiertage
    year  => Jahreszahl ab 1970
    state => Bundesland als offizielle Abkürzung oder Vollname
    """
    try:
        year = int(year)
        if year < 1970:
            year = 1970
            print ('Jahreszahl wurde auf 1970 geändert')
    except ValueError:
        print ('Fehlerhafte Angabe der Jahreszahl')
        return
    if state:
        if state in state_codes.keys():
            state_code = state_codes[state]
        else:
            if state.upper() in state_codes.values():
                state_code = state.upper()
            else:
                state_code = None
    else:
        state_code = None
    if not state_code:
        print ('Es werden nur die deutschlandweit gültigen Feiertage ausgegeben')
    hl = Holidays(year, state_code)
    print(year, state_code)
    holidays = hl.get_holiday_list()
    for h in holidays:
        print (h[1],Holidays.get_day(h[0]), h[0])

    return None

class Holidays:
    """
    Berechnet die Feiertage für ein Jahr. Wird ein Bundesland übergeben, werden
    alle Feiertage des Bundeslandes zurückgegeben. Das erfolgt über die
    Funktion get_holiday_list().
    Das Bundesland (state_code) muss mit der offiziellen zweistelligen
    Bezeichnung übergeben werden (z.B. Sachsen mit SN)

    Holidays(year(int), [state_code(str)])
    """
    def __init__(self, year, state_code):
        self.year = int(year)
        if self.year < 1970:
            self.year = 1970
        if state_code:
            self.state_code = state_code.upper()
            if self.state_code not in state_codes.values():
                self.state_code = None
        self.easter_date = self.get_easter_date(self.year)
        self.holiday_list = []
        self.general_public_holidays(state_code)
        if state_code:
            self.get_three_kings(state_code)
            self.get_assumption_day(state_code)
            self.get_reformation_day(state_code)
            self.get_world_children_day(state_code)
            self.get_all_saints_day(state_code)
            self.get_repentance_and_prayer_day(state_code)
            self.get_corpus_christi(state_code)

    """Gibt anhand des übergebenen Datetime Object (YYYY, MM, DD)
    den passenden Wochentag als Wort zurück"""
    def get_day(date):
        wday = date.weekday()
        if wday == 6:
            day = "Sonntag"
        elif wday == 0:
            day = "Montag"
        elif wday == 1:
            day = "Dienstag"
        elif wday == 2:
            day = "Mittowch"
        elif wday == 3:
            day = "Donnerstag"
        elif wday == 4:
            day = "Freitag"
        else:
            day = "Samstag"
        return day

#    """Prüfen ob angegebenes Datum (Datetime Object (YYYY-MM-DD)) in der Liste der Feiertage ist"""
    def is_holiday(date, year, state_code):

        hl = Holidays(year, state_code)
        print(year, state_code)
        holidays = hl.get_holiday_list()
        for h in holidays:
            print (h[1], h[0])
            if date == h[0]:
                return True
            else:
                return False

    def get_holiday_list(self):
        """
        Gibt die Liste mit den Feiertagen zurück
        """
        self.holiday_list.sort()
        return self.holiday_list

    def general_public_holidays(self, state_code = None):

        """
        Alle einheitlichen Feiertage werden der Feiertagsliste
        zugefügt.
        """
        newyear = datetime.date(self.year, 1, 1)
        self.holiday_list.append([newyear, u'Neujahr'])

        may = datetime.date(self.year, 5, 1)
        self.holiday_list.append([may, u'Tag der Arbeit'])

        if state_code in ['BW','BY', 'BE','BB', 'HB', 'HH','HE', 'MV', 'NI','NW','RP', 'SL','SN', 'SA', 'SH','TH']:#nur Deutschland
            union = datetime.date(self.year, 10, 3)
            self.holiday_list.append([union, u'Tag der deutschen Einheit'])

        christmas1 = datetime.date(self.year, 12, 25)
        if state_code in [ 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W']:#Andrer Name in Österreich
            self.holiday_list.append([christmas1, u'Christtag'])
        elif state_code in ['KZH','KZH','KBE','KLU','KUR','KSZ','KOW','KNW','KGL','KZW','KFR','KSO','KBS','KBS','KBL', 'KSH','KAR','KAI','KSG','KGR','KAG','KTG','KTI','KVD','KVS','KNE','KGE','KJU']:#Andrer Name in der Schweiz
            self.holiday_list.append([christmas1, u'Weihnachtstag'])
        else:
            self.holiday_list.append([christmas1, u'1. Weihnachtsfeiertag'])

        christmas2 = datetime.date(self.year, 12, 26)
        if state_code in [ 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W']:#Andrer Name in Österreich
            self.holiday_list.append([christmas2, u'Stefanietag'])
        elif state_code in ['KZH','KZH','KBE','KLU','KUR','KSZ','KOW','KNW','KGL','KZW','KFR','KSO','KBS','KBS','KBL', 'KSH','KAR','KAI','KSG','KGR','KAG','KTG','KTI']:#Andrer Name in der Schweiz
            self.holiday_list.append([christmas1, u'Stephanstag'])
        else:
            self.holiday_list.append([christmas2, u'2. Weihnachtsfeiertag'])

        """
        Alle festen, individuelllen Feiertage werden der Feiertagsliste zugefügt:
        """

        if state_code in ['K','ST','T', 'V']:#nur Teile von Österreich
            josef = datetime.date(self.year, 3, 19)
            self.holiday_list.append([josef, u'Josef'])

        if state_code in ['O']:#nur Teile von Österreich
            florian = datetime.date(self.year, 5, 4)
            self.holiday_list.append([florian, u'Florian'])

        if state_code in ['S']:#nur Teile von Österreich
            rupert = datetime.date(self.year, 9, 24)
            self.holiday_list.append([rupert, u'Rupert'])

        if state_code in ['K']:#nur Teile von Österreich
            dofv = datetime.date(self.year, 10, 10)
            self.holiday_list.append([dofv, u'Tag der Volksabstimmung'])

        if state_code in ['B','K', 'N','O', 'S', 'ST','T', 'V', 'W']:#nur Teile von Österreich
            nft = datetime.date(self.year, 10, 24)
            self.holiday_list.append([nft, u'Nationalfeiertag'])

        if state_code in ['B']:#nur Teile von Österreich
            martin = datetime.date(self.year, 11, 11)
            self.holiday_list.append([martin, u'Martin'])

        if state_code in ['N','W']:#nur Teile von Österreich
            leopold = datetime.date(self.year, 11, 15)
            self.holiday_list.append([leopold, u'Leopold'])

        if state_code in ['B','K', 'N','O', 'S', 'ST','T', 'V', 'W','KLU','KUR', 'KSZ','KOW', 'KNW', 'KZG','KFR', 'KSO', 'KAI', 'KGR', 'KAG', 'KTI', 'KVS']:#nur Teile von Österreich, Schweiz
            maria = datetime.date(self.year, 12, 8)
            self.holiday_list.append([maria, u'Maria Empfaengnis'])

        if state_code in ['B','K', 'N','O', 'S', 'ST','T', 'V', 'W']:#nur Teile von Österreich
            sylvester = datetime.date(self.year, 12, 31)
            self.holiday_list.append([sylvester, u'Sylvester'])

        """Alle beweglichen Feiertage werden berechnet und der Liste hinzugefügt:"""
        self.holiday_list.append([self.get_holiday(3, _type='minus'), u'Karfreitag'])#D, A. CH
        self.holiday_list.append([self.get_holiday(2, _type='minus'), u'Karfreitag'])#D, A. CH
        self.holiday_list.append([self.easter_date, u'Ostersonntag'])#D, A. CH
        self.holiday_list.append([self.get_holiday(1), u'Ostermontag'])#D, A. CH
        self.holiday_list.append([self.get_holiday(39), u'Christi Himmelfahrt'])#D, A. CH
        self.holiday_list.append([self.get_holiday(49), u'Pfingstsonntag'])#D, A. CH
        self.holiday_list.append([self.get_holiday(50), u'Pfingstmontag'])#D, A. CH


    def get_holiday(self, days, _type='plus'):

        """
        Berechnet anhand des Ostersonntages und der übergebenen Anzahl Tage
        das Datum des gewünschten Feiertages. Mit _type wird bestimmt, ob die Anzahl
        Tage addiert oder subtrahiert wird.
        """
        delta = datetime.timedelta(days=days)
        if _type == 'minus':
            return self.easter_date - delta
        else:
            return self.easter_date + delta

    def get_three_kings(self, state_code):
        """ Heilige Drei Könige """
        """ Oesttereicher Tage hinzugefuegt ab 4."""
        valid = ['BY', 'BW', 'ST', 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W']
        if state_code in valid:
            three_kings = datetime.date(self.year, 1, 6)
            self.holiday_list.append([three_kings, u'Heilige Drei Könige'])

    def get_assumption_day(self, state_code):
        """ Mariä Himmelfahrt """
        """ Oesttereicher Tage hinzugefuegt ab 3."""
        """ Schweizer Tage hinzugefuegt ab 11."""
        valid = ['BY', 'SL', 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W','KLU','KUR', 'KSZ','KOW','KNW','KZG','KFR','KSO','KBL','KAI','KGR','KAG','KTI','KVS','KJU']
        if state_code in valid:
            assumption_day = datetime.date(self.year, 8, 15)
            self.holiday_list.append([assumption_day, u'Mariä Himmelfahrt'])

    def get_reformation_day(self, state_code):
        """ Reformationstag """
        valid = ['BB', 'MV', 'SN', 'ST', 'TH']
        if state_code in valid:
            reformation_day = datetime.date(self.year, 10, 31)
            self.holiday_list.append([reformation_day, u'Reformationstag'])
            
    def get_world_children_day(self, state_code):
        """ Weltkindertag """
        valid = ['TH']
        if state_code in valid:
            worldchildren_day = datetime.date(self.year, 9, 20)
            self.holiday_list.append([worldchildren_day, u'Weltkindertag'])        

    def get_all_saints_day(self, state_code):
        """ Allerheiligen """
        """ Oesttereicher Tage hinzugefuegt ab 6."""
        """ Schweizer Tage hinzugefuegt ab 15."""
        valid = ['BW', 'BY', 'NW', 'RP', 'SL', 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W','KLU','KUR','KSZ','KOW','KNW','KGL', 'KZG','KFR','KSO','KAI','KSG','KGR','KAG','KTI','KVS','KJU']
        if state_code in valid:
            all_saints_day = datetime.date(self.year, 11, 1)
            self.holiday_list.append([all_saints_day, u'Allerheiligen'])

    def get_repentance_and_prayer_day(self, state_code):
        """
        Buß und Bettag
        (Mittwoch zwischen dem 16. und 22. November)
        """
        valid = ['SN']
        if state_code in valid:
            first_possible_day = datetime.date(self.year, 11, 16)
            rap_day = first_possible_day
            weekday = rap_day.weekday()
            step = datetime.timedelta(days=1)
            while weekday != 2:
                rap_day = rap_day + step
                weekday = rap_day.weekday()
            self.holiday_list.append([rap_day, u'Buß und Bettag'])

    def get_corpus_christi(self, state_code):
        """ Fronleichnam 60 Tage nach Ostersonntag """
        """ Oesttereicher Tage hinzugefuegt ab 7. """
        valid = ['BW','BY','HE','NW','RP','SL', 'B','K', 'N','O', 'S', 'ST','T', 'V', 'W']
        if state_code in valid:
            corpus_christi = self.get_holiday(60)
            self.holiday_list.append([corpus_christi, u'Fronleichnam'])


    def get_easter_date(self, year):
        """ Berechnung Ostersonntag nach Lichtenberg """
        """ (http://de.wikipedia.org/wiki/Gau%C3%9Fsche_Osterformel)"""
        """(Korrektur wenn Ostersonntag nach dem 25.April"""

        a = self.year % 19
        k = self.year // 100
        m = 15 + (3 * k + 3) // 4 - (8 * k + 13) // 25
        d = (19 * a + m) % 30
        s = 2 - ( 3 * k + 3) // 4
        r = (d + a // 11) // 29
        og = 21 + d -r
        sz = 7 - (self.year  + self.year  // 4 + s) % 7
        oe = 7 - (og - sz) % 7
        os = (og + oe)
        month, day = divmod(os, 31)
        month = month + 3
        easter_day = datetime.date(self.year, month, day)
        return easter_day

#holidays = Holidays(2021, 'TH')
#liste = holidays.get_holiday_list()
#print(liste)