import os
import time
import sqlite3
import logging

class DataBaseHandler():

    def __init__(self,path_to_data_base):
        sql_create_table = """ CREATE TABLE IF NOT EXISTS objects
        (
            id integer PRIMARY KEY,
            Timestamp DATETIME,
            trafficlight integer DEFAULT -1,
            number integer DEFAULT 0,
            x integer DEFAULT 0,
            y integer DEFAULT 0,
            w integer DEFAULT 0,
            h integer DEFAULT 0
        )
        """

        # We determine if the database exists
        db_exists = False
        if os.path.exists(path_to_data_base):
            db_exists = True

        # We try to connect, this database asumes the folder paths are already created
        try:
            self.connection = sqlite3.connect(path_to_data_base)
        except Exception as e:
            logging.error("Problem with connection to db "+str(e))
            return None
        
        # We create the table:
        cur = self.connection.cursor()
        if not db_exists:
            logging.info("Connecting to existing Data Base, creating table")
            cur.execute(sql_create_table)

    @staticmethod
    def convert_to_db_datetime(seconds_since_epoch):
        # Converts seconds since epoch to standar ISO 8601: YYYY-MM-DD HH:MM:SS.mmmmmm'
        str_seconds = '{0:.2f}'.format(seconds_since_epoch)
        time_iso_format = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(seconds_since_epoch)) + '.' + str_seconds[-2:]
        return time_iso_format

    def insert_new_element(self,current_time_seconds,state,number,x,y,w,h):
        sql = """INSERT INTO objects(Timestamp,trafficlight,number,x,y,w,h) VALUES (?,?,?,?,?,?,?)"""
        logging.debug(sql)
        cur = self.connection.cursor()
        variables = (DataBaseHandler.convert_to_db_datetime(current_time_seconds), state, number, x, y, w, h)
        cur.execute(sql,variables)
        self.connection.commit()
        logging.debug('LAST WORD ID: '+str(cur.lastrowid))
        return cur.lastrowid

    def close_database(self):
        self.connection.close()