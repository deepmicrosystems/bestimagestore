import os
import time
import sqlite3
import logging
from sqlite3 import Error

from tools.methods import convert_to_db_datetime
from tools.methods import convertir_a_nombre_archivo
from tools.methods import convertir_de_iso8601_a_segundos

class DataBaseHandler():

    def __init__(self,path_to_data_base):
        # Fields:
        self.f0 = "timestamp"
        self.f1 = "trafficlight"
        self.f2 = "number"
        self.f3 = "exist"
        self.f4 = "x"
        self.f5 = "y"
        self.f6 = "w"
        self.f7 = "h"
        sql_create_table = """ CREATE TABLE IF NOT EXISTS objects
        (
            id integer PRIMARY KEY,
            {} DATETIME,
            {} integer DEFAULT -1,
            {} integer DEFAULT 0,
            {} boolean DEFAULT 1,
            {} integer DEFAULT 0,
            {} integer DEFAULT 0,
            {} integer DEFAULT 0,
            {} integer DEFAULT 0
        )
        """.format(self.f0,self.f1,self.f2,self.f3,self.f4,self.f5,self.f6,self.f7)

        # We determine if the database exists
        db_exists = False
        if os.path.exists(path_to_data_base):
            db_exists = True

        logging.info('Path: {}'.format(path_to_data_base))

        # We try to connect, this database asumes the folder paths are already created
        try:
            self.connection = sqlite3.connect(path_to_data_base)
        except Exception as e:
            logging.error("Problem with connection to db "+str(e))
            return None
        
        # We create the table:
        if not db_exists:
            logging.info("Connecting to existing Data Base, creating table")
            cur = self.connection.cursor()
            cur.execute(sql_create_table)

    def insert_new_element(self,current_time_seconds,state,number,x,y,w,h):
        sql = "INSERT INTO objects({},{},{},{},{},{},{},{}) VALUES (?,?,?,?,?,?,?,?)".format(self.f0,self.f1,self.f2,self.f3,self.f4,self.f5,self.f6,self.f7)
        logging.debug(sql)
        cur = self.connection.cursor()
        variables = (convert_to_db_datetime(current_time_seconds), state, number, 1, x, y, w, h)
        cur.execute(sql,variables)
        self.connection.commit()
        logging.debug('LAST WORD ID: '+str(cur.lastrowid))
        return cur.lastrowid

    def get_rows_between_times(self, init_time, end_time):
        """
        Delete images between dates in seconds and update the database
        """
        init_time_iso = convert_to_db_datetime(init_time)
        end_time_iso = convert_to_db_datetime(end_time)
        sql = "SELECT * FROM objects WHERE timestamp > {} AND timestamp < {}".format(init_time_iso,end_time_iso)
        cur = self.connection.cursor()
        cur.execute(sql)
        items = cur.fetchall()
        items_number = len(items)
        logging.debug("Got {} rows between {} and {}".format(items_number, init_time_iso, end_time_iso))
        dates = [item[1] for item in items]
        return dates

    def purge_images_before(self,seconds_epoch):
        files_to_purge = self.get_rows_before_time(seconds_epoch)
        for image_name_in_db in files_to_purge:
            try:
                filename = os.getenv('MOVEMENT_PATH')+'/'+convertir_a_nombre_archivo(convertir_de_iso8601_a_segundos(image_name_in_db))
                logging.debug('Deleting {}*'.format(filename))
                os.system('rm {}*'.format(filename))
                self.update_to_non_existing_file(image_name_in_db)
            except Error as e:
                logging.warning('Could not erase image {} because of {}'.format(image_name_in_db,str(e)))

    def update_to_non_existing_file(self,image_name_in_db):
        sql = "UPDATE objects SET {} = 0 WHERE {} = '{}'".format(self.f3,self.f0,image_name_in_db)
        logging.debug(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()
        logging.debug("Updated {}".format(image_name_in_db))


    def get_rows_after_time(self,seconds_epoch):
        return self._get_rows_compared_to_time(seconds_epoch,after = True)

    def get_rows_before_time(self,seconds_epoch):
        return self._get_rows_compared_to_time(seconds_epoch,after = False)

    def _get_rows_compared_to_time(self, seconds_epoch, after = False):
        """
        This private method compares all rows in a database with a date in seconds (since epoch)
        and returns the dates before or after with existing files
        """
        if after:
            compare_symbol = '>'
        else:
            compare_symbol = '<'

        iso_format_date = convert_to_db_datetime(seconds_epoch)
        sql = "SELECT * FROM objects WHERE timestamp {} '{}' AND exist = 1".format(compare_symbol,iso_format_date)
        cur = self.connection.cursor()
        cur.execute(sql)
        items = cur.fetchall()
        items_number = len(items)
        logging.debug("Got {} rows {} {}".format(items_number,compare_symbol,iso_format_date))
        dates = [item[1] for item in items]
        return dates

    def close_database(self):
        self.connection.close()