import psycopg2
import mysql.connector
import logging
import json


class MySQLConnection(object):

    def __init__(self):

        logger = logging.getLogger("mysql_database")

        self.logger = logger

        with open("functions/info", "r", encoding="utf8") as file:
            config = file.read().splitlines()
            self.host = config[0]
            self.user = config[1]
            self.password = config[2]
            self.database = config[3]
            file.close()

    def connect(self):
        try:
            conn = mysql.connector.connect(host=self.host,
                                           user=self.user,
                                           password=self.password,
                                           database=self.database)
            if conn.is_connected():
                user = conn.cursor(buffered=True)
                logging.debug("#Garr's mod: Cursor of database has loaded.")

                user.execute("SET NAMES 'latin1'")
                logging.debug("#Garr's mod: Encoding of database has changed to \"latin1\".")

                conn.commit()
                logging.debug("#Garr's mod: Database with Garry's mod information has successfully connected.")

                return conn, user

        except mysql.connector.Error as error:
            self.logger.error(error)

        except Exception as error:
            self.logger.debug(error)

    def close_conn(self, conn, user):
        try:
            user.close()
            logging.debug("#Garr's mod: Cursor has unloaded.")
        except mysql.connector.Error as error:
            self.logger.error(error)
        except Exception as error:
            self.logger.debug(error)

        try:
            conn.close()
            logging.debug("#Garr's mod: Connection has unloaded.")
        except mysql.connector.Error as error:
            self.logger.error(error)
        except Exception as error:
            self.logger.debug(error)


class PgSQLConnection(object):

    def __init__(self):

        logger = logging.getLogger("pgsql_database")

        self.logger = logger

        with open("functions/info", "r", encoding="utf8") as file:
            config = file.read().splitlines()
            self.host = config[4]
            self.user = config[5]
            self.password = config[6]
            self.database = config[7]
            file.close()

    def _show_tables(self, user):
        try:
            user.execute("SELECT * FROM info")
        except Exception as error:
            self.logger.error(error)
            return True

        return False

    def connect(self):
        try:
            conn = psycopg2.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database)
            user = conn.cursor()

            return conn, user

        except Exception as error:
            self.logger.exception("Database connect")

    def close_conn(self, conn, user):
        try:
            user.close()
        except mysql.connector.Error as error:
            self.logger.error(error)

        try:
            conn.close()
        except mysql.connector.Error as error:
            self.logger.error(error)
