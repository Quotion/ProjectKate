import psycopg2
import mysql.connector
import logging


class MySQLConnection(object):

    def __init__(self):

        logger = logging.getLogger("mysql_database")
        logger.setLevel(logging.INFO)

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
                self.logger.info("Database, with steam data about users, successfully loaded.")
                user = conn.cursor(buffered=True)

                user.execute("SET NAMES 'latin1'")
                conn.commit()

                return conn, user

        except mysql.connector.Error as error:
            self.logger.error(error)

    def close_conn(self, conn, user):
        try:
            user.close()
            self.logger.info("Cursor successfully close.")
        except mysql.connector.Error as error:
            self.logger.error(error)

        try:
            conn.close()
            self.logger.info("Connection successfully close.")
        except mysql.connector.Error as error:
            self.logger.error(error)


class PgSQLConnection(object):

    def __init__(self):

        logger = logging.getLogger("pgsql_database")
        logger.setLevel(logging.INFO)

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
            self.logger.info("Connection PostgreSQL successfully establishment.")
            user = conn.cursor()

            return conn, user

        except psycopg2.extensions as error:
            self.logger.error(error)

    def close_conn(self, conn, user):
        try:
            user.close()
            self.logger.info("Cursor successfully close.")
        except mysql.connector.Error as error:
            self.logger.error(error)

        try:
            conn.close()
            self.logger.info("Connection successfully close.")
        except mysql.connector.Error as error:
            self.logger.error(error)
