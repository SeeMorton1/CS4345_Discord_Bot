import mysql.connector
from dotenv import load_dotenv
import os
from pytz import timezone
import datetime



class database_func:
    __instance = None

    @staticmethod
    def getInstance():
        # singleton pattern to make sure only
        # one instance of database connection is running
        if database_func.__instance is None:
            database_func()
        return database_func.__instance


    def __init__(self):
        # establish database conection
        if database_func.__instance is None:
            load_dotenv()
            connection_config_dict = {
                'user': os.getenv('ROOT'),
                'password': os.getenv('PASSWORD'),
                'host': os.getenv('HOST'),
                'database': os.getenv('DATABASE'),
                'raise_on_warnings': True,
            }
            self.connection = mysql.connector.connect(**connection_config_dict)
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                self.cursor = self.connection.cursor()
            database_func.__instance = self
        else:
            print("This is singleton, you cannot have multiple objects")


    def add_user(self, userid, username):
        # insert a user into the user table given
        # userid username
        insert_stmt = "insert ignore into Users (user_id, username)""Values (%s,%s)"
        data = (userid, username)
        self.cursor.execute(insert_stmt, data)
        self.connection.commit()
        print("Inserted successfully")

    def add_class(self, class_name:str, channel_id:int, role_id:int, user_id:int):
        # insert a class
        insert_stmt = "insert into Classes (channel_id, class_name, role_id, user_id)""Values (%s,%s,%s,%s)"
        data = (channel_id,class_name,role_id,user_id)
        self.cursor.execute(insert_stmt, data)
        self.connection.commit()

    def add_enrollment(self, user_id, class_id):
        # add user enrollment to a class
        insert_stmt = "insert into Enrollments (user_id, class_id, date_enrolled)""Values (%s, %s, NOW())"
        data = (user_id, class_id)
        self.cursor.execute(insert_stmt, data)
        self.connection.commit()
        print("Inserted successfully")

    # add_task will add a task to the table Tasks. Tasks has these columns: task_id(The discord message id), user_id(the discord author id), channel_id(the discord channel id), task_name(the task name), task_description(the details of the task), difficulty(int 1-10),deadline(the deadline of the task)
    def add_task(self, task_id, user_id, channel_id, task_name, task_description, difficulty, deadline):
        insert_stmt = "insert into Tasks (task_id, user_id, channel_id, task_name, task_description, difficulty, deadline)""Values (%s, %s, %s, %s, %s, %s, %s)"
        data = (task_id, user_id, channel_id, task_name, task_description, difficulty, deadline)
        self.cursor.execute(insert_stmt, data)
        self.connection.commit()
        print("Inserted successfully")
        
    #get_tasks_channel_specific will return all the tasks in a specific channel and specific user, it takes in a channel id, user id, and the number of days to look forward
    def get_tasks_channel_specific(self, channel_id, user_id, days):
        select_stmt = "SELECT * from Tasks t where t.channel_id = %s and t.user_id = %s and DATEDIFF(t.deadline,NOW()) < %s"
        data = (channel_id, user_id, days)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results
    def get_tasks_user_all(self, user_id,days):
        select_stmt = "SELECT * from Tasks t where t.user_id = %s and DATEDIFF(t.deadline,NOW()) < %s"
        data = (user_id,days)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results

    def update_task_deadline(self, user_id, taskname, new_deadline):
        # change task dealdine
        update_stmt = "update Tasks set deadline = %s where task_name = %s and user_id =%s;"
        data = (new_deadline, taskname, user_id)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update %s successfully" % taskname)
        
    def delete_user(self, userid):
        # delete a user
        delete_stmt = "delete from Users where user_id = %s"
        data = (userid,)
        self.cursor.execute(delete_stmt, data)
        self.connection.commit()
        print("delete successfully")

    def delete_class(self, class_name):
        # delete a class
        delete_stmt = "delete from Classes where class_name = %s"
        data = (class_name,)
        self.cursor.execute(delete_stmt, data)
        self.connection.commit()
        print("delete %s successfully" % class_name)

    def delete_task(self,task_name):
        # delete a task
        delete_stmt = "delete from Tasks where task_name = %s"
        data = (task_name)
        self.cursor.execute(delete_stmt, data)
        self.connection.commit()
        print("delete %s successfully" % task_name)
    
    def delete_expired_tasks(self):
        # delete all expired tasks
        delete_stmt = "delete from Tasks where deadline < NOW()"
        self.cursor.execute(delete_stmt)
        self.connection.commit()
        print("delete expired tasks successfully")

    def users_in_class(self, class_id):
        select_stmt = "select Users.username from Users join Enrollments on Users.user_id = Enrollments.user_id where Enrollments.class_id =%s"
        data = (class_id,)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results

    def print_all_users(self):
        select_stmt = "select username from Users"
        self.cursor.execute(select_stmt)
        results = self.cursor.fetchall()
        return results

    def print_all_class(self):
        select_stmt = "select* from Classes"
        self.cursor.execute(select_stmt)
        results = self.cursor.fetchall()
        for x in results:
            print(x)

    def update_user(self,name,server,time_zone):
        # update user info
        update_stmt = "update Users set username = %s , servers = %s, time_zone = %s where username = %s;"
        data = (name,server,time_zone)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update %s successfully" % name)

    def update_class(self,classname,server):
        # update class info
        update_stmt = "update Classes set class_name = %s, servers = %s where class_name =%s"
        data = (classname,server)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update %s successfully" % classname)

    def clear_activity(self):
        delete_stmt = "truncate table Activities"
        self.cursor.execute(delete_stmt)
        self.connection.commit()
        print("clear activity successfully")

    def add_activity(self, userid, activity):
        # add user activity
        insert_stmt = "insert into Activities (user_id,activity)""Values (%s,%s)"
        data = [userid, activity]
        self.cursor.execute(insert_stmt, data)
        self.connection.commit()
        print("Inserted " + activity + " successfully")

    def update_activity(self,userid,activity):
        # update user activity
        update_stmt = "update Activities set time = time+10 where user_id =%s and activity =%s"
        data = (userid,activity)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update %s successfully" % activity)

    def activity_exist(self, userid, activity):
        select_stmt = "SELECT * from Activities where user_id = %s and activity = %s"
        data = (userid, activity)
        self.cursor.execute(select_stmt,data)
        results = self.cursor.fetchall()
        if len(results) == 0:
            return False
        else:
            return True

    def get_user_activities(self,userid):
        # return all users activity
        select_stmt = "SELECT activity, time from Activities where user_id = %s"
        data = (userid, )
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results
    # here we return list of tuples

    def sum_user_activities(self,userid):
        # sum their activity
        select_stmt = "select sum(time) from Activities where user_id = %s and activity not like %s"
        data = (userid,"%custom%" )
        self.cursor.execute(select_stmt, data)
        result = self.cursor.fetchone()[0]
        if result is None:
            result = 0
        return result

    def get_playtime_limit_and_warning(self,userid):
        # prepare to warn user
        select_stmt = "SELECT playtime_limit, is_warned from Users where user_id =%s"
        data = (userid, )
        self.cursor.execute(select_stmt, data)
        result = self.cursor.fetchone()
        return result
    # return a tuple where [0] is limit and [1] is warned or not
    def is_warned(self,userid):
        # make them warned to prevent spamming
        update_stmt = "update Users set is_warned =1 where user_id =%s"
        data = (userid,)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update successfully")
    #     the user is warned

    def change_warned(self,userid):
        # change warning status daily
        update_stmt = "update Users set is_warned =0 where user_id =%s"
        data = (userid,)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update successfully")
    #     change warning status
    def change_play_time_limit(self, userid, time):
        # update playtime limit
        update_stmt = "update Users set playtime_limit =%s where user_id =%s"
        data = (time, userid)
        self.cursor.execute(update_stmt, data)
        self.connection.commit()
        print("update successfully")



    def add_reminder(self,reminder_id, channel_id, user_id, reminder_time, title, description):
        # create a reminder
        insert_stmt = "insert into Reminders (reminder_id, channel_id, user_id, reminder_time, reminder_title,reminder_description)""Values (%s,%s,%s,%s,%s,%s)"
        data = [reminder_id , channel_id , user_id , reminder_time , title, description]
        self.cursor.execute(insert_stmt,data)
        self.connection.commit()
        print("Inserted reminder successfully")

    def get_reminders(self):
        # get pending reminders
        select_stmt = "select channel_id, reminder_title, reminder_description from Reminders where reminder_time BETWEEN %s AND %s"
        now_time = datetime.datetime.now(timezone('America/Chicago'))
        past_time = now_time - datetime.timedelta(minutes=1)
        now = now_time.strftime('%Y-%m-%d-%H:%M:%S')
        past = past_time.strftime('%Y-%m-%d-%H:%M:%S')
        data = (past, now)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results
    #     return lists of approached reminders

    def add_meeting(self, meeting_id, channel_id, title, begin, end, location, description, creator):
        # create a meeting
        insert_stmt = "insert into Meetings ""Values (%s,%s,%s,%s,%s,%s,%s,%s)"
        data = [meeting_id, channel_id, title, begin, end, location, description, creator]
        self.cursor.execute(insert_stmt,data)
        self.connection.commit()
        print("Inserted meeting successfully")

    def get_meetings(self):
        # get meetings arrived
        select_stmt = "select meeting_id, channel_id, meeting_title, begin_time, end_time,location, description  from Meetings where begin_time BETWEEN %s AND %s"
        now_time = datetime.datetime.now(timezone('America/Chicago'))
        past_time = now_time - datetime.timedelta(minutes=1)
        now = now_time.strftime('%Y-%m-%d-%H:%M:%S')
        past = past_time.strftime('%Y-%m-%d-%H:%M:%S')
        data = (past, now)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results

    def get_meetings_within_10minutes(self):
        # get meetings within 10 minutes
        select_stmt = "select meeting_id, channel_id, meeting_title, begin_time, end_time, location from Meetings where begin_time BETWEEN %s AND %s"
        now_time = datetime.datetime.now(timezone('America/Chicago'))
        time_change = datetime.timedelta(minutes=10)
        future_time = now_time + time_change
        now = now_time.strftime('%Y-%m-%d-%H:%M:%S')
        future = future_time.strftime('%Y-%m-%d-%H:%M:%S')
        data = (now, future)
        self.cursor.execute(select_stmt, data)
        results = self.cursor.fetchall()
        return results

    def add_participant_to_meetings(self, user_id,meeting_id):
        # add users to participation table
        insert_stmt = "insert into Participation (user_id, meeting_id) ""Values (%s,%s)"
        data = [user_id,meeting_id]
        self.cursor.execute(insert_stmt,data)
        self.connection.commit()
        print("Inserted participants successfully")


    def disconnect(self):
        # make sure to disconnect database after finish everything
        self.cursor.close()
        self.connection.close()
