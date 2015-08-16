#TODO:
#	 1.Support writing CSVpath in entry, right now only the Browse Button actually sets path.
#	 2. In the Name Entry, hide text while it is in focus, and show previous text, if nothing new has been inputed when the entry is no longer in focus
#	 3. Consider if some dialog box should warn, if the competition name is not unique, when compared to existing events in the DB
#	 4. Add scrollbar to listbox if it exceeds size
#	 5. Use correct OS.split, to ensure cross-platform compatibility

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showwarning
from dbTools import csv2db

class ImportCSV(Frame, csv2db):
	def __init__(self, parent=None, **options):
		csv2db.__init__(self, dbPath='data/event.db')
		Frame.__init__(self, parent, **options)
		parent.title("Import CSV to Database")
		self.CompetitionTypes=['Fast Catch', 'Trick Catch', 'MTA', 'Long Distance', 'Endurance', 'Aussi Round', 'Accuracy']
		self.makeWidgets(parent)

	def makeWidgets(self,parent):
		self.columnconfigure(0, pad=10)
		Label(self, text="Competition Type:").grid(row=0, column=0, sticky=W)
		self.listbox = Listbox(self)
		self.listbox.grid(row=1, column=0, rowspan=5)
		for item in self.CompetitionTypes:
		    self.listbox.insert(END, item)

		Label(self, text="Competition Name:").grid(row=0, column=1, sticky=W+S)
		self.CompNameEnt = Entry(self, width=30)
		self.CompNameEnt.insert(0, 'Enter a name for the competition')
		self.CompNameEnt.grid(row=1, column=1, columnspan=2, sticky=W)

		Label(self, text="CSV file path:").grid(row=2, column=1, sticky=W+S)
		self.CompPathEnt = Entry(self)
		self.CompPathEnt.insert(0, "Choose CSV file")
		self.CompPathEnt.grid(row=3, column=1, sticky=W)
		self.isTeamEvent = IntVar()
		Checkbutton(self, text='Team Event',
						  variable=self.isTeamEvent).grid(row=4, column=1, sticky=W)
		Button(self, text='Import', command=self.importPressed).grid(row=5, column=1, sticky=E)
		Button(self, text='Browse', command=self.Browse).grid(row=3, column=2)
		Button(self, text='Cancel', command=parent.quit).grid(row=5, column=2)

	def importPressed(self):
		try:
			self.importFromCSV()
		except:
			showwarning('Mising information','Please make sure you have selected\na Competition Type, Competition Name and a valid CSV file. Then try again')


	def Browse(self):
		self.CSVpath = askopenfilename(filetypes=[("CSV-files", "*.csv"),("Plain text", "*.txt")])
		if(self.CSVpath): #Only updates entry text if a new value is selected
			self.CompPathEnt.delete(0,END)
			self.CompPathEnt.insert(0,self.CSVpath.split('/')[-1])

	#Overwrites method for dbTools.csv2db
	def add2Eventlist(self):
		#Tries to insert the event and throws an error if the event has already been loaded.
		try:
			self.CompetitionType = self.CompetitionTypes[int(self.listbox.curselection()[0])]
			self.TeamEvent = str(self.isTeamEvent.get())
			self.cursor.execute('insert into Events ( CompetitionName, FilePath, CompetitionType, TeamEvent) values(?,?,?,?)', (self.CompNameEnt.get(), self.CSVpath,self.CompetitionType, '1'))
			self.db.commit()
			return True
		except:
			return False

	#Overwrites method for dbTools.csv2db
	def errCSVDublette(self):
		showwarning('Dublette warning','The CSV file you are importing, has been previously import. \nDublettes are not allowed.')

if __name__ == '__main__': 
	root = Tk()
	ImportCSV(root).pack(fill=BOTH, expand=YES)
	root.mainloop()