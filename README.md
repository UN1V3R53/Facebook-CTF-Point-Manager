# Facebook-CTF-Point-Manager

![image](https://user-images.githubusercontent.com/38517436/61676123-c581c980-ad35-11e9-80f0-09e1d2ab14c8.png)

Facebook-CTF-Point-Manager 이 툴은 Flag 값 공유를 막기 위한 목적으로 개발 되었다.

최근에 나오는 CTF 대회는 어떤 문제를 여러 팀이 풀었을 경우, 이 문제를 푼 팀의 점수와 그 문제의 점수가 같이 떨어지게 된다. 하지만 Faceboot CTF template은 그렇지 않다.

그래서 이 툴을 이용하면 어떤 문제를 여러 팀이 풀었을 때, 이 문제를 푼 팀의 점수와 그 문제의 점수가 같이 떨어지게끔 만들어져 있다.

아래 영상은 위 설명을 영상으로 나타낸 것이다.


[![Video Label](https://img.youtube.com/vi/NDHIUlJtXBM/0.jpg)](https://youtu.be/NDHIUlJtXBM)



# How to Use

우선 fbctf_pointManager.py 와 fbctfDB.py를 다운 받는다.

이 툴을 사용하기 전에 fbctfDB.py 파일을 수정 해야 한다.

아래 코드는 fbctfDB.py에서 43 ~ 51번째 줄에 해당하는 코드이다.

우리가 수정해야 할 부분은 44 ~ 47번 째 줄이다. 이는 DB와 연결을 하기 위한 계정 정보를 입력하는 곳이다.
```python
try:
	host = "localhost"
	mysql_id = "root"
	mysql_pw = "root"
	dbname = "fbctf"
	conn = pymysql.connect(host = host, user = mysql_id, password = mysql_pw, db = dbname, charset = "utf8")
	db = conn.cursor(pymysql.cursors.DictCursor)
except Exception as err:
	print("[!] \x1b[1;31mError\x1b[1;m: ",err)
```


그 다음 이 툴을 실행하기 전에 아래 사진 처럼 Facebook CTF 관리자 페이지에서 BEGIN GAME 을 클릭한다.

![image](https://user-images.githubusercontent.com/38517436/61676458-f9a9ba00-ad36-11e9-8058-0e026a241490.png)





아래 사진처럼 fbctf_pointManager.py 를 실행한다.

실행 옵션은 --id와 --pw인데 이 계정 정보는 facebook ctf 관리자 페이지에 접근 할 수 있는 계정이어야 한다.

![image](https://user-images.githubusercontent.com/38517436/61676538-51e0bc00-ad37-11e9-9e6f-da4ae803a9f3.png)





위와 같이 실행을 하게 되면 아래 사진처럼 실행이 되고, 1초에 한번씩 누가 문제를 풀었는지 모니터링을 하게 된다.

![image](https://user-images.githubusercontent.com/38517436/61676598-8f454980-ad37-11e9-97f2-4b6cc83a72f4.png)




만약 어떤 사람이 문제를 풀었다면 아래 사진처럼 log가 기록이 된다.

어떤 문제의 점수가 떨어졌고, 어떤 유저의 점수가 떨어지는지 확인 할 수 있다.

![image](https://user-images.githubusercontent.com/38517436/61676630-af750880-ad37-11e9-8479-d3592be7b4e2.png)
