#!/usr/bin/env python2.6
# coding: utf-8

import sqlite3
import re
import sys, os
from optparse import OptionParser
from groparser import parse_entry


DICTIONARIES = {
	'en': 'Engelsk',
	'de': 'Tysk',
	'fr': 'Fransk',
	'es': 'Spansk',
	'se': 'Svensk',
}


def print_entries(raw_entries):
	"""Nasty, semi-succesfuld formatering af rå artikeldata
	
	Du har ikke lyst til at vide hvad der foregår her!"""
	for entry in raw_entries:
		entry = entry[8:]
		entry = entry.split('\0')[-2]
		text = entry
		text = re.sub(r'<h3>.*?</h3>', '\n', text)
		text = re.sub(r' *<(?!/ol|ol|ul|/ul|li|/li).*?>', ' ', text)
		text = re.sub(r'<(/?\w+).*?>', r'<\1>', text)
		text = re.sub(r' +', ' ', text)
		text = re.sub(r'^\s*', '', text)
		text = re.sub(r'(?<=>) *| *(?=<)', '', text)
		i = 0
		output = ""
		indentwidth = 4
		indent = -1
		while i < len(text):
			if text[i:].startswith(r'<ol>') or text[i:].startswith(r'<ul>'):
				indent += 1
				i += 4
			elif text[i:].startswith(r'</ol>') or text[i:].startswith(r'</ul>'):
				indent -= 1
				i += 5
			elif text[i:].startswith(r'<li>'):
				output += '\n' + ' '*indentwidth*indent
				i += 4
			elif text[i:].startswith(r'</li>'):
				i += 5
			else:
				output += text[i]
				i += 1
		output = output.replace('&lt;', '<')
		output = output.replace('&gt;', '>')
		print output


def search(db, dictionary_path, search_terms, table, fromDanish):
	"""Slå søgetermerne op i ordbogen og hent de matchende artikler.

	Funktionen returnerer en liste af rå artikeldata for hvert artikelmatch
			
	db = database
	search_terms = liste af søgetermer
	table = navn på tabel i databasen, hvor søgetermerne skal findes
	fromDanish = hvilken retningen slår vi op i ordbogen?"""

	# find id for matchende artikler
	fromDanish = 1 if fromDanish else 2;
	first_term = True
	for term in search_terms:
		rows = list(db.execute('select * from %s%i where word_ like \'%s\''
				%(table,fromDanish,term)))
		term_entry_ids = [r[0] for r in rows]
		if first_term:
			first_term = False
			entry_ids = term_entry_ids			
		else:
			entry_ids = set(term_entry_ids) & set(entry_ids)

	# hent artikeldata
	raw_entries = []
	for entry_id in entry_ids:
		rows = list(db.execute('select * from entries%i where id_ = %d'
				%(fromDanish, entry_id)))
		for _, entry_type, link_id, offset, nbyte in rows:
			raw_entry = parse_entry(dictionary_path+'.dat',entry_id, offset, nbyte)
			raw_entries.append(raw_entry)
	return raw_entries


def lookup(dictionary_path, search_terms, foreign_language):	
	"""Foretag søgning i ordbogen

	Funktionen printer de fundne resultater til terminalen

	dictionary_path = sti til ordbogsfilerne (uden .dat og .gdd suffix)
	search_terms = liste af søgetermer
	foreign_language = tekstreng med det fremmede sprogs navn"""

	db = sqlite3.connect(dictionary_path+'.gdd')

	search_terms = [s.replace('*','%').replace('\'',' ').replace('.','%')
			for s in search_terms]
	
	print '=== Opslagsord fra Dansk-%s:'%foreign_language
	raw_entries = search(db, dictionary_path, search_terms, 'lookup', True)
	if raw_entries:
		print_entries(raw_entries)
	else:
		print '(intet fundet)'
	
	print '\n\n=== Opslagsord fra %s-Dansk:'%foreign_language
	raw_entries = search(db, dictionary_path, search_terms, 'lookup', False)
	if raw_entries:
		print_entries(raw_entries)
	else:
		print '(intet fundet)'
	# Bemærk at vi ikke slår ordforbindelser op. Dette gøres ved at benytte
	# tabellerne 'collocation_lookup'. Derudover kan man slå bagvendt op i
	# ordbogen ved at benytte tabellerne 'reverse'. Se mere i databasefilen!
		

def main():
	# parse programargumenter
	usage = u'Usage: %prog [options] SEARCH_STRING'
	description=u'Blå og brugervenlig ordbog'
	parser = OptionParser(description=description, usage=usage)
	parser.add_option('-l', '--lang', nargs=1,
			default='en', dest='lang', choices=DICTIONARIES.keys(),
			help=u'language (en, de, fr, es, se)')
	parser.add_option('-p', '--path', nargs=1, default='./',
			dest='path', help='path to data files (.dat and .gdd)')	
	args,search_terms = parser.parse_args()
	if len(search_terms) == 0:
		parser.print_help()
		sys.exit(1)
	language = DICTIONARIES[args.lang]
	dictionary_path = os.path.join(args.path,language+'Ordbog')
	if not os.path.isfile(dictionary_path+'.gdd'):
		print "Fejl, ordbogsdata ikke fundet: " + dictionary_path+'[.gdd|.dat]'
		sys.exit(1)
	# søg!
	lookup(dictionary_path, search_terms, language)

	
if __name__ == '__main__':
	main()

