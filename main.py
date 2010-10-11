#!/usr/bin/env python2.6
# coding: utf-8

import os
import gui
import dictionary

# Angiv stierne til ordbogsfilerne nedenfor. 
# Udkommenter sprog som du ikke ønsker at bruge
dictionaries = {
	'en': {
		'name': 'Engelsk',
		'gddfile': 'data/EngelskOrdbog.gdd',
		'datfile': 'data/EngelskOrdbog.dat',
	},
	'de': {
		'name': 'Tysk',
		'gddfile': 'data/TyskOrdbog.gdd',
		'datfile': 'data/TyskOrdbog.dat',
	},
	'fr': {
		'name': 'Fransk',
		'gddfile': 'data/FranskOrdbog.gdd',
		'datfile': 'data/FranskOrdbog.dat',
	},
	'es': {
		'name': 'Spansk',
		'gddfile': 'data/SpanskOrdbog.gdd',
		'datfile': 'data/SpanskOrdbog.dat',
	},
	'se':  {
		'name': 'Svensk',
		'gddfile': 'data/SvenskOrdbog.gdd',
		'datfile': 'data/SvenskOrdbog.dat',
	},
}

def main():

	# check om sprogene er tilgængelige
	filenotfound = False
	for d in dictionaries.keys():
		lang = dictionaries[d];
		if not (os.path.exists(lang['gddfile']) and os.path.exists(lang['datfile'])):
			print 'Ordbogsfiler for %s kan ikke findes i mappen %s'%(lang['name'],os.path.dirname(os.path.abspath(lang['gddfile'])))
			filenotfound = True
	if filenotfound:
		return
	dic = dictionary.Dictionary(dictionaries)
	dictionaryGUI = gui.DictionaryGUI(dic)
	dictionaryGUI.run()


if __name__ == '__main__':
	main()

