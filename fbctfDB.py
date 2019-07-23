from sys import exit
import pymysql
import time
import requests
import bs4
import urllib3 
urllib3.disable_warnings (urllib3.exceptions.InsecureRequestWarning)

'''
>> DESC `teams`
	+---------------+--------------+------+-----+---------------------+-----------------------------+
	| Field         | Type         | Null | Key | Default             | Extra                       |
	+---------------+--------------+------+-----+---------------------+-----------------------------+
	| id            | int(11)      | NO   | PRI | NULL                | auto_increment              |
	| active        | tinyint(1)   | NO   | MUL | 1                   |                             |
	| name          | varchar(255) | NO   |     | NULL                |                             |
	| password_hash | varchar(255) | NO   |     | NULL                |                             |
	| points        | int(11)      | NO   |     | 0                   |                             |
	| last_score    | timestamp    | NO   |     | CURRENT_TIMESTAMP   | on update CURRENT_TIMESTAMP |
	| logo          | text         | NO   |     | NULL                |                             |
	| admin         | tinyint(1)   | NO   |     | 0                   |                             |
	| protected     | tinyint(1)   | NO   |     | 0                   |                             |
	| visible       | tinyint(1)   | NO   | MUL | 1                   |                             |
	| created_ts    | timestamp    | NO   |     | 0000-00-00 00:00:00 |                             |
	+---------------+--------------+------+-----+---------------------+-----------------------------+
'''


if __name__ == "__main__":
	print("[\x1b[1;31m!\x1b[1;m] Do not execute me directly!")
	exit()


userID = "reloading"
userPW = "$2y$12$bk9Vp4Z8n.P0aDGC.ilVkeBdq5r7gBD22bi9U15cdFq63nQIYvcI2"  #  real_PW: reloading!@#



################
#  DB connect  #
################
# Referer: http://pythonstudy.xyz/python/article/202-MySQL-%EC%BF%BC%EB%A6%AC
try:
	host = "localhost"
	mysql_id = "root"
	mysql_pw = "root"
	dbname = "fbctf"
	conn = pymysql.connect(host = host, user = mysql_id, password = mysql_pw, db = dbname, charset = "utf8")
	db = conn.cursor(pymysql.cursors.DictCursor)
except Exception as err:
	print("[!] \x1b[1;31mError\x1b[1;m: ",err)


#########################
#   ID duplicate Check  #
#########################
def duplicateCheck():
	# Id duplicate check
	sql = "SELECT name FROM teams WHERE name=%s"
	db.execute(sql,(userID))	# Run query
	rows = db.fetchall()	# Get query result
	conn.commit()

	return rows


##############################
#  Create user 'reloading'   #
##############################
def createUser():
	rows = duplicateCheck()

	if rows:	# This case is that "reloading" id was already existed.
		return 0
	else:
		sql = "SELECT id FROM teams ORDER BY id DESC LIMIT 0,1"
		db.execute(sql)
		rows = db.fetchall()

		userIndex = int(rows[0]['id']) + 1

		sql = "INSERT INTO teams VALUES("+str(userIndex)+", 1, '"+userID+"', '"+userPW+"', 0, SYSDATE(), '8ball', 0, 0, 0, SYSDATE())"
		db.execute(sql)
		conn.commit()
		rows = db.fetchall()

		return userIndex



def getTeams():
	sql = "SELECT id, name, points FROM teams WHERE visible=1"
	db.execute(sql)
	rows = db.fetchall()
	conn.commit()

	return rows


def activityLogMonitor():
	sql = "SELECT id, subject, action, entity, ts FROM activity_log where action='captured' ORDER BY id"
	db.execute(sql)
	rows = db.fetchall()
	conn.commit()

	return rows


def getChallengePoints():
	sql = "SELECT entity_id, points FROM levels ORDER BY entity_id"
	db.execute(sql)
	rows = db.fetchall()
	conn.commit()

	return rows

def modifyPoints(activityLog, countriesInfo, penalty, csrf, s):
	# Get all challenges infomation using requests module.
	# Because korea language is broken using mysql query.
	print("[\x1b[1;33m*\x1b[1;m] Getting all challenges information...")

	while True:
		try:
			req = s.get('https://localhost/index.php?p=admin&page=flags', verify=False)
			reqChallenge = bs4.BeautifulSoup(req.content, 'html.parser', from_encoding='euc-kr')
			reqChallenge = reqChallenge.find_all('section', {'class':'validate-form admin-box section-locked'})
			getChallengeInfo = {}

			for i in range(len(reqChallenge)):
				tmp = reqChallenge[i].find('form', {'class' : 'level_form flag_form'})
				challengeID = int(tmp.find('input', {'name':'level_id'}).get('value'))
				challengeTitle = tmp.find('input', {'name' : 'title'}).get('value')
				tmpDescription = str(tmp.find('textarea',{'name' : 'description'}))
				challengeDescription = tmpDescription[tmpDescription.find('>')+1:tmpDescription.find('</textarea>')]
				challengeFlag = tmp.find('input',{'name' : 'flag'}).get('value')

				getChallengeInfo[challengeID] = {'title' : challengeTitle, 'description' : challengeDescription, 'flag' : challengeFlag}
			break
		except Exception as err:
			print("[\x1b[1;31m!\x1b[1;m] \x1b[1;31mError\x1b[1;m: ", err)
			print("[\x1b[1;33m*\x1b[1;m] Retry request...")
	print("[\x1b[1;32m*\x1b[1;m] Successfully get all challenges information.")

	# Choose 'first solver' or 'not first solver'
	# And accept modified points.
	log = activityLog[0]
	solve_teamID = log['subject'][log['subject'].find(':')+1:]
	solve_countryID = int(log['entity'][log['entity'].find(':')+1:])
	before_points = countriesInfo[solve_countryID]['point']

	print('\n[\x1b[1;33m*\x1b[1;m] Modifying points of user and challenge...')
	try:	# Not first solver
		if countriesInfo[solve_countryID]['solve']:
			teamID_list = countriesInfo[solve_countryID]['solve']					

			for teamID in teamID_list:
				sql = "SELECT points, name FROM teams WHERE id=%s"
				db.execute(sql,(teamID))
				rows = db.fetchall()
				conn.commit()
				userName = rows[0]['name']


				points = int(eval(str(rows[0]['points']) + str(penalty)))

				sql = "UPDATE teams SET points=%s WHERE id=%s"
				db.execute(sql, (points, teamID))
				conn.commit()

				print("[\x1b[1;32m*\x1b[1;m] Modified {} user:  {} pts => {}".format(userName, rows[0]['points'], points))

			countriesInfo[solve_countryID]['solve'].append(solve_teamID)
			countriesInfo[solve_countryID]['point'] = int(eval(str(countriesInfo[solve_countryID]['point'])+str(penalty)))
	except KeyError:	# First solver
		countriesInfo[solve_countryID]['solve'] = []
		countriesInfo[solve_countryID]['solve'].append(solve_teamID)
		countriesInfo[solve_countryID]['point'] = int(eval(str(countriesInfo[solve_countryID]['point'])+str(penalty)))	# penalty points

	# Set modified points
	sql = "UPDATE levels SET points=%s WHERE entity_id=%s"
	db.execute(sql,(countriesInfo[solve_countryID]['point'], solve_countryID))
	conn.commit()


	# Reloading Challenge (Request to web server)
	sql = "SELECT entity_id, category_id, id, title, description, flag FROM levels WHERE entity_id=%s"
	db.execute(sql,{solve_countryID})
	rows = db.fetchall()
	conn.commit()

	datas = {
		'action' : 'update_flag',
		'title' : getChallengeInfo[rows[0]['id']]['title'],
		'description' :	 getChallengeInfo[rows[0]['id']]['description']+' ',
		'flag' : 	getChallengeInfo[rows[0]['id']]['flag'],
		'entity_id' : rows[0]['entity_id'],
		'category_id' : rows[0]['category_id'],
		'points' : countriesInfo[solve_countryID]['point'],
		'bonus' : 0,
		'bonus_dec' : 0,
		'hint' : '',
		'penalty': 0,
		'level_id' : rows[0]['id'],
		'csrf_token' : csrf
	}

	req = s.post('https://localhost/index.php?p=admin&ajax=true', data = datas, verify=False)
	if req.text.find("OK") != -1:
		# Announcment result
		title = getChallengeInfo[rows[0]['id']]['title'][:20]

		print('[\x1b[1;32m*\x1b[1;m] Successfully Modifying points.')
		print("     {}...: {} points => {} points\n".format(title, before_points, countriesInfo[solve_countryID]['point']))
	else:
		print("[\x1b[1;31m!\x1b[1;m] Error. Can't update the country's points.")

	return countriesInfo