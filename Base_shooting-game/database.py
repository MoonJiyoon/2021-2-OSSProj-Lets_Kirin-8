import pymysql
import bcrypt
import pygame

pygame.mixer.init()


class Database(object): 
    def __init__(self,host='database-1.c79ahye2go7m.ap-northeast-2.rds.amazonaws.com',user='admin',password='letskirin',db='hiScores',charset='utf8'):
        self.scoreDB=pymysql.connect(host=host,user=user,password=password,db=db,charset=charset)
        self.curs = self.scoreDB.cursor()
        self.numScores=15

    def id_not_exists(self,input_id):
        sql="SELECT * FROM users WHERE user_id=%s"
        self.curs.execute(sql,input_id)
        data=self.curs.fetchone()
        self.curs.close()
        if data:
            return False
        else:
            return True
        
    def compare_data(self, id_text, pw_text): # 데이터베이스의 아이디와 비밀번호 비교
        input_password=pw_text.encode('utf-8')
        curs = self.scoreDB.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM users WHERE user_id=%s"
        curs.execute(sql,id_text)
        data = curs.fetchone()
        curs.close()
        check_password=bcrypt.checkpw(input_password,data['user_password'].encode('utf-8'))
        return check_password

    def add_id_data(self,user_id): # 아이디 추가
        sql = "INSERT INTO users (user_id) VALUES (%s)"
        self.curs.execute(sql, user_id)
        self.scoreDB.commit()  #서버로 추가 사항 보내기
        self.curs.close()

    def add_password_data(self,user_password,user_id): # 비밀번호 추가
        new_salt=bcrypt.gensalt()
        new_password=user_password.encode('utf-8')
        hashed_password=bcrypt.hashpw(new_password,new_salt)
        decode_hash_pw=hashed_password.decode('utf-8')
        self.curs = self.scoreDB.cursor()
        sql = "UPDATE users SET user_password= %s WHERE user_id=%s"
        self.curs.execute(sql,(decode_hash_pw,user_id))
        self.scoreDB.commit()  #서버로 추가 사항 보내기
        self.curs.close()  

    def getSound(self,music=False):
        if music:
            self.curs.execute("CREATE TABLE if not exists music (setting integer)")
            self.curs.execute("SELECT * FROM music")
        else:
            self.curs.execute("CREATE TABLE if not exists sound (setting integer)")
            self.curs.execute("SELECT * FROM sound")
        self.scoreDB.commit()
        setting = self.curs.fetchall()
        self.curs.close()
        return bool(setting[0][0]) if len(setting) > 0 else False

    def setSound(self,setting, music=False):
        if music:
            self.curs.execute("DELETE FROM music")
            self.curs.execute("INSERT INTO music VALUES (%s)", (setting,))
        else:
            self.curs.execute("DELETE FROM sound")
            self.curs.execute("INSERT INTO sound VALUES (%s)", (setting,))
        self.scoreDB.commit()
        self.curs.close()

    def getScores(self):
        self.curs.execute('''CREATE TABLE if not exists scores
                     (name text, score integer, accuracy real)''')
        self.curs.execute("SELECT * FROM scores ORDER BY score DESC")
        self.scoreDB.commit()
        hiScores = self.curs.fetchall()
        self.curs.close()
        return hiScores

    def setScore(self,hiScores,name, score, accuracy):
        sql="SELECT * FROM scores WHERE name=%s"
        self.curs.execute(sql,name)
        data=self.curs.fetchone()
        
        if data:
            self.curs.close()
            return 
        else:
            print(hiScores)
            if len(hiScores) >= self.numScores:
                lowScoreName = hiScores[-1][0]
                lowScore = hiScores[-1][1]
                sql="DELETE FROM scores WHERE (name = %s AND score = %s)"
                self.curs.execute(sql,(lowScoreName,lowScore))
            sql="INSERT INTO scores VALUES (%s,%s,%s)"
            self.curs.execute(sql,(name, score, accuracy))
            self.scoreDB.commit()
            self.curs.close()
    
    def getTimeScores(self): #For TimeMode
        self.curs.execute('''CREATE TABLE if not exists scores
                     (name text, score integer, accuracy real)''')
        self.curs.execute("SELECT * FROM scores ORDER BY score DESC")
        self.scoreDB.commit()
        hiScores = self.curs.fetchall()
        self.curs.close()
        return hiScores
    
    def setTimeScore(self,hiScores,name, score, accuracy): #For TimeMode
        sql="SELECT * FROM scores WHERE name=%s"
        self.curs.execute(sql,name)
        data=self.curs.fetchone()
        
        if data:
            self.curs.close()
            return 
        else:
            print(hiScores)
            if len(hiScores) >= self.numScores:
                lowScoreName = hiScores[-1][0]
                lowScore = hiScores[-1][1]
                sql="DELETE FROM scores WHERE (name = %s AND score = %s)"
                self.curs.execute(sql,(lowScoreName,lowScore))
            sql="INSERT INTO scores VALUES (%s,%s,%s)"
            self.curs.execute(sql,(name, score, accuracy))
            self.scoreDB.commit()
            self.curs.close()
    

