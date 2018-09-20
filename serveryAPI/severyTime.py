"north", "seibel", "baker", "sidrich", "south", "west"

dayToNum = {
	"U" : 0,
	"M" : 1,
	"T" : 2,
	"W" : 3,
	"R" : 4,
	"F" : 5,
	"S" : 6

}

dayToDay = {
	"U" : "sunday",
	"M" : "monday",
	"T" : "tuesday",
	"W" : "wednesday",
	"R" : "thursday",
	"F" : "friday",
	"S" : "saturday"
}

mealToNum = {
	"breakfast" : 0,
	"brunch" : 1,
	"lunch" : 2,
	"dinner" : 3
}


def timeToDay (time):
	#input: a string, 2018-09-15T00:00:00.000-05:00, output: a string day
	return dayToDay[time[10:11]];

def timeFormat (time):
	#input: a string, 2018-09-15T00:00:00.000-05:00, output: (miliseconds after 00:00:00.000, dayNumber)
	
	raw_time = time[11:19]
	formated_time = hmsToMs(raw_time)
	dayNumber = dayToNum[time[10:11]];

	return (formated_time, dayNumber)

def hmsToMs (time):
	#input: a string, 00:00:00, output: a integer, miliseconds after 00:00:00.000
	
	hrs, mins, secs = time.split(":")
	formated_time = int(hrs)*360000 + int(mins) * 6000 + int(secs) * 100

	return formated_time

#0 is sunday, 1 workday, 6 is saturday
serveryByDay =	{
	"0": [(), ("north", "south", "seibel", "west"), (), ("north", "south", "seibel", "west")],
	"1": [("north", "seibel", "baker", "sidrich", "south", "west"), (), ("north", "seibel", "baker", "sidrich", "south", "west"), ("north", "seibel", "baker", "sidrich", "south", "west")],
    "6": [("north", "seibel"), (), ("north", "seibel"), ("north", "seibel")]
}

serveryByTime = {
	"baker" : [[(), (), (), ()], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(), (), (), ()]],
	"north" : [[(), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (), (hmsToMs ("17:00:00"), hmsToMs ("19:00:00"))], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(hmsToMs ("09:00:00"), hmsToMs ("11:00:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (hmsToMs ("16:45:00"), hmsToMs ("18:15:00"))]],
	"sidrich" : [[(), (), (), ()], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(), (), (), ()]],
	"south" : [[(), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (), (hmsToMs ("17:00:00"), hmsToMs ("19:00:00"))], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(), (), (), ()]],
	"west" : [[(), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (), (hmsToMs ("17:00:00"), hmsToMs ("19:00:00"))], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(), (), (), ()]],
	"seibel" : [[(), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (), (hmsToMs ("17:00:00"), hmsToMs ("19:00:00"))], [(hmsToMs ("07:30:00"), hmsToMs ("09:30:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("13:30:00")), (hmsToMs ("17:30:00"), hmsToMs ("19:30:00"))], [(hmsToMs ("09:00:00"), hmsToMs ("11:00:00")), (), (hmsToMs ("11:30:00"), hmsToMs ("14:00:00")), (hmsToMs ("16:45:00"), hmsToMs ("18:15:00"))]],
	
}

def getServeryTimeTable (serveryName):
	#input a string for servery name, return a list of tuple of time range, time in ms
	return serveryByTime[serveryName];


def filterByDay (time):
	#input a time string, return list of servery open during these day 
	current_day = timeFormat(time)[1];
	if (1 <= current_day and current_day <= 5):
		return serveryByDay["1"]
	return serveryByDay[str(current_day)]



def filterByTime (time):
	#input a time string, return list of servery open during this time
	current_time = timeFormat(time)[0]
	current_day = timeFormat(time)[1]

	available_severy = set()
	open_today = filterByDay(time)
	for serveries_of_meal in open_today:
		for servery in serveries_of_meal:
			if(CheckOneServery(time, servery)):
				available_severy.add(servery)
	return available_severy

def CheckOneServery (time, serveryName):
	#input a string for servery name, return a boolean
	current_time = timeFormat(time)[0]
	current_day = timeFormat(time)[1] 
	if (1 <= current_day and current_day <= 5):
		#work day
		current_servery_time = serveryByTime[serveryName][1]
	elif (current_day == 6):
		#Saturday
		current_servery_time = serveryByTime[serveryName][2]
	else :
		#Sunday
		current_servery_time = serveryByTime[serveryName][0] 
	availability = False
	for meal in current_servery_time:
		if(meal and current_time >= meal[0] and current_time <= meal[1]):
			availability = True
	return availability


def filterByMeal (time, mealName):
	#input a string fro meal name, breakfast, lunch, dinner, brunch, return a dictionary of servery as key and time range tuple as value
	current_day = timeFormat(time)[1]
	mealNum = mealToNum[mealName]
	open_today = filterByDay(time)

	return open_today[mealNum]





	
