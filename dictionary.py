# coding: utf-8

import sys, os
import sqlite3
import re
from array import array
import groparser


class Dictionary:
	def __init__(self, dictionaries):
		self.dictionaries = dictionaries

	def get_dictionaries(self):
		return self.dictionaries


	def getEntries(self, db, search_terms, table, fromDanish):
		'''Slå søgetermerne op i ordbogen og hent de matchende artikler.

		Funktionen returnerer en liste af rå artikeldata for hvert artikelmatch
			
		db = database
		search_terms = liste af søgetermer
		table = navn på tabel i databasen, hvor søgetermerne skal findes
		fromDanish = hvilken retningen slår vi op i ordbogen?'''

		# TODO: dette her burde kunne gøres i en enkelt SQL statement
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

		entries = []
		for entry_id in entry_ids:
			rows = list(db.execute('select * from entries%i where id_ = %d'
					%(fromDanish, entry_id)))
			for _, entry_type, link_id, offset, nbyte in rows:
				entries.append((entry_id, offset, nbyte))
		return entries

	def getRawEntryText(self, dat_file, entries):
		raw_entries = []
		for entry_id, offset, nbyte in entries:
			data = self.extractFromFile(dat_file, offset, nbyte)
			raw_entry = groparser.parse_entry(data, entry_id, offset, nbyte)
			raw_entries.append(raw_entry.split('\0')[-2])
		return raw_entries

	def extractFromFile(self, f, offset, nbyte):
		f.seek(offset)
		data = array('B')
		data.fromfile(f, nbyte)
		return data

	def lookup(self, search_terms, language):	
		'''Foretag søgning i ordbogen

		Funktionen printer de fundne resultater til terminalen

		dictionary_path = sti til ordbogsfilerne (uden .dat og .gdd suffix)
		search_terms = liste af søgetermer
		language = tekstreng med det fremmede sprogs navn'''

		# make * and . wildcard letters;  strip ' characters to avoid SQL injections
		search_terms = [s.replace('*','%').replace('\'',' ').replace('.','%')
				for s in search_terms]

		# open data files
		db_path = self.dictionaries[language]['gddfile']
		dat_path = self.dictionaries[language]['datfile']
		dat_file = open(dat_path, 'rb')
		db = sqlite3.connect(db_path)

		# search and collect results
		results = {'fromDanish': {}, 'toDanish': {}}
		tables = ['lookup', 'reverse', 'collocation_lookup']
		directions = [(True, 'fromDanish'),(False, 'toDanish')]
		for d, d_name in directions:
			for t in tables:
				if t == 'reverse' or t == 'collocation_lookup':
					d = not d
				entries = self.getEntries(db, search_terms, t, d)
				entrytexts = self.getRawEntryText(dat_file, entries)
				results[d_name][t] = entrytexts

		dat_file.close()
		return results

