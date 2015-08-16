#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

#----------------- Algoritmen forklaret ------------------#
#Foerst hentes alle scores ud i et array
#arrayet sorteres og checkes igennem for draws
#placeringerne laegges i et nyt array
#deltagerne sorteres efter score og placeringen indskrives.

class Participant:
	def __init__(self, participantID, score):
		self.ID = participantID
		self.score = score
	def __repr__(self):
		return repr((self.ID, self.score))


class CalculatePlacing:
	def __init__(self, eventDbPath):
		self.db = sqlite3.connect(eventDbPath)
		self.cursor = self.db.cursor()

		self.size=0


	def evaluate(self, competitionID):
		self.participant_objects=[]
		self.noValidTime=[]
		self.not_participants_objects=[]
		self.scores=[]
		self.scoresNoValidTime=[]
		self.cursor.execute('select CompetitionType from Events where ID=?', (competitionID))
		self.competitionType = self.cursor.fetchone()[0]

		if self.competitionType in ['Accuracy','Aussi Round','Trick Catch']:
			self.unit  = 'points'
			self.highIsBest = True
		elif self.competitionType=='Endurance':
			self.unit  = 'caught'
			self.highIsBest = True
		elif self.competitionType=='MTA':
			self.unit = 'seconds'
			self.highIsBest = True
		elif self.competitionType=='Fast Catch':
			self.unit = 'seconds'
			self.highIsBest = False
		elif self.competitionType=='Long Distance':
			self.unit = 'meters'
			self.highIsBest = True
		else: 
			print('Bad competition type argument, Check Case.\nThe following competitions are supported: Accuracy, Aussi Round, Trick Catch, Fast Catch, Endurance, MTA, Long Distance')

		self.cursor.execute('select P_ID,Score from Scores where Event_ID=?', (competitionID))
		participants = self.cursor.fetchall()


		for row in participants:
			row=list(row)
			try:
				if self.competitionType=='Fast Catch' or self.competitionType=='MTA':
					row[1]=float(row[1])
				else:
					row[1]=int(row[1])

				if row[1]==0: #checks for zero points
					self.noValidTime.append(Participant(row[0],str(row[1])))
					self.scoresNoValidTime.append(str(row[1]))

				else: # normal points
					self.participant_objects.append(Participant(row[0],row[1]))
					self.scores.append(row[1])

			except:

				if 'c' in row[1] or 'C' in row[1]: #Checks for catches
					row[1]=row[1].split()[0]+' Caught'
					self.noValidTime.append(Participant(row[0],row[1]))
					self.scoresNoValidTime.append(row[1])

				else: #else np
					self.not_participants_objects.append(Participant(row[0],row[1]))

		#normal score is sorted		
		self.scores = sorted(self.scores, reverse=self.highIsBest)
		self.participant_objects = sorted(self.participant_objects, key=lambda participant: participant.score, reverse=self.highIsBest)
		#special catches is sorted in reversed order
		try:self.scoresNoValidTime = sorted(self.scoresNoValidTime, reverse=True)
		except:
			print(self.scoresNoValidTime)
			print("Type: "+type(self.scoresNoValidTime))
			quit()

		self.noValidTime = sorted(self.noValidTime, key=lambda participant: participant.score, reverse=True)
		#arrays are joined
		self.scores += self.scoresNoValidTime
		self.participant_objects += self.noValidTime



		#BUG: Last places missing if scores are equal
		#Returns an array following the syntax:
		#[place,placementpoints]
		#-------- Generates first occurence array for placements -------------#=
		placingAndPoints=[]
		placementFirstOccur=[]
		placementFirstOccur.append(1)
		for i in range (1,len(self.participant_objects)):
			if self.scores[i-1]!=self.scores[i]:
				placementFirstOccur.append(i+1)
		# Adds a last entry to make shure second last element can be calculated. This could be the 
		# NP's first occurrence. 
		placementFirstOccur.append(len(self.participant_objects)+1)

		#--------- Generates placement and placement points -------#
		# runs through every tiebreak
		for x in range(0,len(placementFirstOccur)-1):
			#Calulates the mean of placement points.
			spaces = placementFirstOccur[x+1]-placementFirstOccur[x]
			score = float(placementFirstOccur[x])
			for y in range(1,spaces):
				score+=(placementFirstOccur[x]+y)
			score=score/spaces
			#writes out result "space"'s'times
			for z in range(1,spaces+1):
				placingAndPoints.append([placementFirstOccur[x],score])


		i=0
		for participant in self.participant_objects:
			###Write the update SQL CALL
			self.cursor.execute("update Scores set Placing=?,PlacingPoints=? WHERE P_ID=? and Event_ID=?",(placingAndPoints[i][0],placingAndPoints[i][1],participant.ID, competitionID))
			self.db.commit()
			i+=1

		i=0
		for participant in self.not_participants_objects:
			self.cursor.execute("update Scores set Placing=?,PlacingPoints=? WHERE P_ID=? and Event_ID=?",('np',self.getSize(),participant.ID, competitionID))
			self.db.commit()
			i+=1

	def getSize(self):
		self.size = len(self.participant_objects)+len(self.not_participants_objects)
		return self.size

CalculatePlacing('data/event.db').evaluate('1')
CalculatePlacing('data/event.db').evaluate('2')

			