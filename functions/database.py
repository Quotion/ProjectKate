import psycopg2
import mysql.connector
import logging


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
                user.execute("SET NAMES 'latin1'")
                conn.commit()
                # user.execute("SET CHARACTER SET 'latin1'")
                # conn.commit()
                logging.debug("#Garry's mod: Cursor of database has loaded.")

                return conn, user

        except mysql.connector.Error as error:
            self.logger.error(error)

        except Exception as error:
            self.logger.error(error)

    def close_conn(self, conn, user):
        try:
            user.close()
            logging.debug("#Garry's mod: Cursor has unloaded.")
        except mysql.connector.Error as error:
            self.logger.warning(error)
        except Exception as error:
            self.logger.debug(error)

        try:
            conn.close()
            logging.debug("#Garry's mod: Connection has unloaded.")
        except mysql.connector.Error as error:
            self.logger.warning(error)
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

    def connect(self):
        try:
            conn = psycopg2.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database)
            user = conn.cursor()

            return conn, user

        except Exception:
            self.logger.exception("Database not connect")

    def close_conn(self, conn, user):
        try:
            user.close()
        except mysql.connector.Error as error:
            self.logger.warning(error)

        try:
            conn.close()
        except mysql.connector.Error as error:
            self.logger.warning(error)
