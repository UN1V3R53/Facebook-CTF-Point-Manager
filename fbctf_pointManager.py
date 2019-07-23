from sys import exit
import fbctfDB
import requests
import argparse
import time
import datetime
import urllib3 
import bs4
urllib3.disable_warnings (urllib3.exceptions.InsecureRequestWarning)

duplicate_check_msg ='''
┌──────────────────────┐
│  ID Duplicate Check  │
└──────────────────────┘
'''
reloading_msg = '''\n\n
┌────────────────────┐
│  Reloading points  │
└────────────────────┘
'''
mornitor_msg = '''\n\n
┌─────────────────────────────┐
│  Monitoring Activity Logs   │
└─────────────────────────────┘
'''


def systemTime():
	now = datetime.datetime.now()
	return "[\x1b[1;32m*\x1b[1;m] Start time : "+now.strftime('%Y-%m-%d %H:%M:%S')

def countries():	# Config countries id, countries points and solved user id.
	countries_info = {}
	countries_tmp = {} 	# tmp

	challengePoints = fbctfDB.getChallengePoints()
	for i in range(len(challengePoints)):
		countries_tmp[challengePoints[i]['entity_id']] = challengePoints[i]['points']

	for i in range(1,177):
		try:
			countries_info[i] = {'point' : countries_tmp[i]}
		except KeyError:
			countries_info[i] = {}

	return countries_info

def reloading(userIndex, csrfToken, activityLog, countriesInfo, penalty, s):
	# Modiry user's points and challenge's points.
	countriesInfo = fbctfDB.modifyPoints(activityLog, countriesInfo, penalty, csrfToken, s)

	url = "https://localhost/index.php?p=admin&ajax=true"
	datas_visibility = {'action':'toggle_visible_team', 'team_id':userIndex, 'visible':1, 'csrf_token':csrfToken}
	datas_invisibility = {'action':'toggle_visible_team', 'team_id':userIndex, 'visible':0, 'csrf_token':csrfToken}

	## Setting visible
	print('[\x1b[1;33m*\x1b[1;m] Setting "visible : 1" option of "reloading" user... ')
	while True:
		try:
			req = s.post(url, data = datas_visibility, verify=False)
			if req.text.find("OK") != -1:
				print("[\x1b[1;32m*\x1b[1;m] Successfully set visible.")
				break
			else:
				print("[\x1b[1;31m!\x1b[1;m] \x1b[1;31mError\x1b[1;m: ",req.text)
				print("[\x1b[1;33m*\x1b[1;m] Retry request...")

		except Exception as err:
			print("[\x1b[1;31m!\x1b[1;m] \x1b[1;31mError\x1b[1;m: ",err)
			print("[\x1b[1;33m*\x1b[1;m] Retry request...")

	time.sleep(1)

	## Setting invisible
	print('[\x1b[1;33m*\x1b[1;m] Setting "visible : 0" option of "reloading" user... ')
	while True:
		try:
			req = s.post(url, data = datas_invisibility, verify=False)
			if req.text.find("OK") != -1:
				print("[\x1b[1;32m*\x1b[1;m] Successfully set invisible.")
				break
			else:
				print("[\x1b[1;31m!\x1b[1;m] \x1b[1;31mError\x1b[1;m: ",req.text)
				print("[\x1b[1;33m*\x1b[1;m] Retry request...")

		except Exception as err:
			print("[\x1b[1;31m!\x1b[1;m] \x1b[1;31mError\x1b[1;m: ",err)
			print("[\x1b[1;33m*\x1b[1;m] Retry requet...")
			
	return countriesInfo


def WebSession(id, pw):
	s = requests.Session()
	datas = {'action' : 'login_team', 'team_name' : parse.id, 'password' : parse.pw}
	req = s.post('https://localhost/index.php?p=index&ajax=true', data = datas, verify=False)
	req = s.post('https://localhost/index.php?p=admin')

	result = bs4.BeautifulSoup(req.content, 'html.parser', from_encoding='euc-kr')
	csrf = result.find('input', {'name' : 'csrf_token'}).get('value')

	return s, csrf


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--id', help = "[*] Input the CTF admin ID.")
	parser.add_argument('--pw', help = "[*] Input the CTF admin PW.")
	parser.add_argument('--penalty', help = "[*] Not essence(Only number). Setting penalty. Default value: -10 points")
	parse = parser.parse_args()

	if not parse.id:
		print("[\x1b[1;31m!\x1b[1;m] Input the CTF admin ID.")
		exit()
	if not parse.pw:
		print("[\x1b[1;31m!\x1b[1;m] Input the CTF admin PW.")
		exit()
	if not parse.penalty:
		print("[\x1b[1;33m*\x1b[1;m] Not setting penalty. Default value: -10 points.")
		parse.penalty = "-10"
	else:
		if parse.penalty[:1] == '-' or parse.penalty[:1] == '+':
			print("[\x1b[1;32m*\x1b[1;m] Penalty value : {}".format(parse.penalty))
		else:
			print("[\x1b[1;31m!\x1b[1;m] Check your penalty option value. ex) -10, +10")

	print(duplicate_check_msg+'\n'+systemTime())
	userIndex = fbctfDB.createUser()

	if userIndex == 0:		# This case is that "reloading" user was already existed.
		print("[\x1b[1;33m*\x1b[1;m] \"reloading\" user was already existed.")
	else:
		print("[\x1b[1;32m*\x1b[1;m] \"reloading\" user was created.")

	time.sleep(0.5)

	countriesInfo = countries()
	before = []
	msg_on = 1
	count = 0

	if not fbctfDB.activityLogMonitor():
		while True:
			if count % 600 == 0:
				s, csrf = WebSession(parse.id, parse.pw)
			if msg_on:
				print(mornitor_msg+'\n'+systemTime())
				msg_on = 0

			after = fbctfDB.activityLogMonitor()
			if after:
				msg_on = 1
				print("[\x1b[1;32m*\x1b[1;m] Someone solved challenge.")
				print(reloading_msg+'\n'+systemTime())
				countriesInfo = reloading(userIndex, csrf, after[len(before):len(before)+1], countriesInfo, parse.penalty, s)

				before = after[:len(before)+1]
				break
			time.sleep(1)
			count = count + 1

	while True:
		if count % 600 == 0:
			s, csrf = WebSession(parse.id, parse.pw)
		if msg_on:
			print(mornitor_msg+'\n'+systemTime())
			msg_on = 0
		after = fbctfDB.activityLogMonitor()
		if len(before) != 0 and len(before) != len(after): 
			msg_on = 1

			print("[\x1b[1;32m*\x1b[1;m] Someone solved challenge.")

			print(reloading_msg+'\n'+systemTime())
			countriesInfo = reloading(userIndex, csrf, after[len(before):len(before)+1], countriesInfo, parse.penalty, s)
			before = after[:len(before)+1]
		time.sleep(1)
		count = count + 1