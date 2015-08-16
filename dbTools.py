# TODO:
#	0. Brainstorm and develop the applikation design and UI.
#		0.1 Draw it!
#		0.2 Code it!
# 	1. Create Replace Function, to replace data from an already loaded csv file
# 	2. Create an undo function either here or in GUI file.
#	3. Look for userdefined events in external file
# 	4. Refactor and clean up
#	5. Prepare system for calculating scores based on argument from event db. So new events can be added with ease.
#	6. Design syntax for event 'modding/plugin'-language
#	7. Write parser
#	8. Implement into Score algorithm
#	9. Refactor and clean up
#	10. Test with tournament Data, and correct errors
#	11. Design, develop and implement CERTIFICATES/DIPLOMAS printing and designing system.
#	12. Design, develop and implement Registration Form in tkinter.
#	13. Design, develop and implement Registration Form in PHP.
#	14. Enable software to load from server.
#		14.1 Load registration from server
#		14.2 Create and load Tournament backup
#		14.3 Upload results for website
#		14.4 Enable remote scorekeeping
#		14.5 Show who has payed, and how much
#	15. Improve user interactions, and make sure data can be accesed and edited with ease.
#	16. Design, develop, and implement automatic tournement planner
#	17. Design, develop, and implement Throwing Circle Planner
#	18. Design, develop, and implement Budgeting
#	19. Make ticket system, for print


import csv, sqlite3, os

class csv2db():
	def __init__(self, dbPath='data/event.db'):
		self.db = sqlite3.connect(dbPath)
		self.cursor = self.db.cursor()
		self.CreateTablesInDB()
		self.CSVpath=None
		self.CompetitionName=None
		self.CompetitionType=None
		self.TeamEvent=None

	def __del__(self):
		self.db.close()

	def CreateTablesInDB(self):
		####	Activate foreign key	####
		self.cursor.execute('pragma foreign_keys = ON;')

		####	Create tables			####
		self.cursor.execute('CREATE TABLE IF NOT EXISTS Persons ( ID integer primary key autoincrement, FirstName text not null, LastName text not null, StartNbr integer, EmailAdress text)')
		self.cursor.execute('CREATE TABLE IF NOT EXISTS Events ( ID integer primary key autoincrement, CompetitionName text, FilePath text unique, CompetitionType text, TeamEvent text)')
		self.cursor.execute('CREATE TABLE IF NOT EXISTS Scores ( P_ID integer, Event_ID integer, Score text, Placing integer, PlacingPoints real, foreign key (P_ID) references Persons(ID), foreign key (Event_ID) references Events(ID) )')

	def importFromCSV(self):
		####	Load CSV file		####
		with open(self.CSVpath, newline='', encoding='utf-8') as f:

		####	Count events
			self.cursor.execute('SELECT max(ID) FROM Events')
			max_id = self.cursor.fetchone()[0]
			if(max_id):
				max_id += 1
			else:
				max_id = 1

			if(self.add2Eventlist()):
				#Add new event to database
				reader = csv.reader(f)
				next(reader)
				for row in reader:
					FirstName = str(row[1].split()[0])
					LastName = str(row[1].split()[1])
					StartNbr = int(row[2])
					Score = str(row[3])
					Placing = str(row[4])
					PlacingPoints = float(row[5])

					#Assign points to existing P_ID
					self.cursor.execute('select ID from Persons where FirstName=? and LastName=?', (FirstName, LastName))
					preAssigned_P_ID = self.cursor.fetchone()
					if(preAssigned_P_ID != None):
						self.cursor.execute('insert into Scores (P_ID, Event_ID, Score, Placing, PlacingPoints) values(?, ?, ?, ?, ?)',(preAssigned_P_ID[0], max_id, Score, Placing, PlacingPoints))
						self.db.commit()

					# #Assign points to new P_ID
					else:
						self.cursor.execute('SELECT max(ID) FROM Persons')
						i = self.cursor.fetchone()[0]
						if(i):
							i += 1
						else:
							i = 1

						self.cursor.execute('insert into Persons (FirstName, LastName, StartNbr) values(?, ?, ?)',(FirstName, LastName, StartNbr))
						self.db.commit()
						self.cursor.execute('insert into Scores (P_ID, Event_ID, Score, Placing, PlacingPoints) values(?, ?, ?, ?, ?)',(i, max_id, Score, Placing, PlacingPoints))
						self.db.commit()
			else:
				self.errCSVDublette()

	def add2Eventlist(self):
		#Tries to insert the event and throws an error if the event has already been loaded.
		try:
			self.cursor.execute('insert into Events ( CompetitionName, FilePath, CompetitionType, TeamEvent) values(?,?,?,?)', (self.CompetitionName, self.CSVpath, self.CompetitionType, self.TeamEvent))
			self.db.commit()
			return True
		except:
			return False

	def errCSVDublette(self):
		print('The CSV file you are importing, has been previously import. \nAborting to avoid dubletes')

if __name__ == '__main__':
	root = tkinter.Tk()
	root.withdraw()

