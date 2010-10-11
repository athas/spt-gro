# coding: utf-8
import sys, os
try:
	import gtk
except:
	print 'Fejl, Gtk er ikke installeret'
	sys.exit(1)
import htmltextview
import groparser

graphics_path = 'graphics'
icon_path =  os.path.join(graphics_path,'%s20.png')
dictionary_icon_path = os.path.join(graphics_path,'dictionary.svg')

class DictionaryGUI:
	def __init__(self, dic):
		self.dic = dic
		self.search_results = None
		self.gtkBuilder = gtk.Builder()
		self.gtkBuilder.add_from_file("ui.glade")
		self.txtSearchString = self.gtkBuilder.get_object('txtSearchString')
		self.comboLanguage = self.gtkBuilder.get_object('comboLanguage')
		self.txtContents = self.gtkBuilder.get_object('txtContents')
		self.scrollWindow = self.gtkBuilder.get_object('scrollwindow')
		self.checkFromDanish = self.gtkBuilder.get_object('checkFromDanish')
		self.checkToDanish = self.gtkBuilder.get_object('checkToDanish')
		self.checkExamples = self.gtkBuilder.get_object('checkExamples')
		self.checkReverse = self.gtkBuilder.get_object('checkReverse')
		self.langImage1 = self.gtkBuilder.get_object('langImage1')
		self.langImage2 = self.gtkBuilder.get_object('langImage2')
		self.langImage3 = self.gtkBuilder.get_object('langImage3')
		self.langImage4 = self.gtkBuilder.get_object('langImage4')
		self.winMain = self.gtkBuilder.get_object('winMain')

		self.winMain.set_icon_from_file(dictionary_icon_path)

		# make contents for ComboBox
		self.dictionaries = dic.get_dictionaries()
		contents = []
		for lang in self.dictionaries.keys():
			contents.append([lang, self.dictionaries[lang]['name'], 
					gtk.gdk.pixbuf_new_from_file(icon_path%lang)])
		contents.sort(key=lambda x:x[1])
		# insert content
		self.liststoreLanguages = gtk.ListStore(str,str,gtk.gdk.Pixbuf)
		for c in contents:
			self.liststoreLanguages.append(c)
		self.comboLanguage.set_model(self.liststoreLanguages)
		# layout content
		crp = gtk.CellRendererPixbuf()
		crp.set_property('xalign',0)
		self.comboLanguage.pack_start(crp, False)
		self.comboLanguage.add_attribute(crp, 'pixbuf', 2)
		cell = gtk.CellRendererText()
		self.comboLanguage.pack_start(cell, True)
		self.comboLanguage.add_attribute(cell, 'text', 1)
		self.comboLanguage.set_active(0)

		# set appropriate flags
		self.langImage1.set_from_file(icon_path%'da')
		self.langImage4.set_from_file(icon_path%'da')
		self.updateFlags()


		# attach signal handlers
		signal_dic = { 
				'on_btnSearch_clicked' : self.btnSearch_clicked, 
				'on_winMain_destroy' : gtk.main_quit,
				'on_winMain_key_press_event' : self.winMain_key_press,
				'on_txtSearchString_key_press_event' : self.txtSearchString_key_press,
				'on_comboLanguage_changed' : self.comboLanguage_changed,
				'on_checkExamples_toggled' : self.update_search_results,
				'on_checkReverse_toggled' : self.update_search_results,
				'on_checkFromDanish_toggled' : self.update_search_results,
				'on_checkToDanish_toggled' : self.update_search_results,
		}
		self.gtkBuilder.connect_signals(signal_dic)

		# hack to make height of txtSearchString equal to heigh of 
		# search button and language chooser
		(_, height) = self.comboLanguage.get_child_requisition()
		self.txtSearchString.set_size_request(-1, height+2)

	def winMain_key_press(self, widget, event):
		pass
#		if event.keyval==gtk.keysyms.Return:
#			self.search()

	def update_search_results(self, widget):
		self.show_search_results()

	def comboLanguage_changed(self, widget):
		self.updateFlags()

	def updateFlags(self):
		language = self.get_search_result_language()
		self.langImage2.set_from_file(icon_path%language)
		self.langImage3.set_from_file(icon_path%language)

	def txtSearchString_key_press(self, widget, event):
		if event.keyval==gtk.keysyms.Return:
			self.search()
		
	def btnSearch_clicked(self, widget):
		self.search()

	def search(self):
		search_terms = self.txtSearchString.get_text().strip().split(' ')
		language = self.get_comboLanguage_language()[0]		
		self.search_results = self.dic.lookup(search_terms, language)
		self.search_results['lang'] = language
		self.show_search_results()
		self.updateFlags()

	def get_comboLanguage_language(self):
		languageIdx = self.comboLanguage.get_active()
		return self.liststoreLanguages[languageIdx]

	def get_search_result_language(self):
		if self.search_results is None:
			# if no search results exists, just return language from combobox
			language = self.get_comboLanguage_language()[0]		
		else: 
			language = self.search_results['lang']
		return language
	
	def language_name(self, lang):	
		return self.dictionaries[lang]['name']
		
	def show_search_results(self):
		if self.search_results == None:
			return
		lang = self.get_search_result_language()
		language_name = self.language_name(lang)
		htmlview = htmltextview.HtmlTextView()
		contents = ''
		directions = []
		if self.checkFromDanish.get_active():
			directions.append(('fromDanish', 'Dansk-%s'%language_name))
		if self.checkToDanish.get_active():
			directions.append(('toDanish', '%s-Dansk'%language_name))
		tables = [('lookup','Artikler')]
		if self.checkReverse.get_active():
			tables.append(('reverse', ''))
		if self.checkExamples.get_active():
			tables.append(('collocation_lookup', 'Eksempelsætninger'))
		for d, d_name in directions:
			contents += '<p style="font-size:12.5pt;font-weight:bold">' + d_name + '</p>'
			for t, t_name in tables:
				if t == 'reverse':
					t_name = 'Forekomster i %s-Dansk'%language_name if d=='fromDanish' else 'Forekomster i Dansk-%s'%language_name
				contents += '<br/><br/><p style="font-size:8pt;font-weight:bold">' + t_name + '</p><br/><br/>'
				entries = self.search_results[d][t]
				for entry in entries:
					contents += groparser.entry_to_html(entry,t)
			contents += '<br/><br/>'
		
		contents = '''<body xmlns='http://www.w3.org/1999/xhtml'>'''+ contents +'''</body>'''

		def handler(texttag, widget, event, iter_, kind, href):
				    if event.type == gtk.gdk.BUTTON_PRESS:
				            print href
		htmlview.html_hyperlink_handler = handler
		htmlview.display_html(contents)

		htmlview.show()
		self.txtContents.set_buffer(htmlview.get_buffer())



	def run(self):
		gtk.main()

