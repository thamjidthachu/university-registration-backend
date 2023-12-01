import cx_Oracle
import logging

logger = logging.getLogger('root')


class Oracle:
    """
        this class is prepared the connection to oracle and execute the commands
    """

    def __init__(self, URI="QABOOL_USER/QABOOL_USER@10.101.1.140:1521/EREGDB", encoding="utf-8"):
        # prepare the connection
        logger.exception("Connection Establishing....")
        prepare = self.prepare_oracle_connection(URI, encoding)
        if prepare is not None:
            self._connection = prepare
            cursor = prepare.cursor()
            if cursor:
                self._cursor = cursor
            else:
                logger.exception("Can't accessed to the cursor")

    def prepare_oracle_connection(self, URI, encoding):
        """
            prepare the connection and check if the connection will be valid or not
        """
        try:
            logger.exception("Prepare Connection....")
            return cx_Oracle.Connection(URI, encoding=encoding)
        except Exception as e:
            logger.exception(f"Exception Occurred - {e}, Can't connect to the server using this link + {self}")

        return

    def _commit_execution(self):
        """
            commit the query only for insert the data
        """
        try:
            self._connection.commit()
            return True
        except Exception as e:
            logger.exception(f"Can't commit the current execution! due to Exception - {e}")
        return

    def close_connection(self):
        """
            close connection after finish the process
        """
        try:
            self._connection.close()
            return True
        except Exception as e:
            logger.exception(f"The current connection can't be closed Due to Exception : {e}")
        return

    def insert(self, query, *args, **kwargs):
        if hasattr(self, "_cursor"):
            try:
                self._cursor.execute(query, *args, **kwargs)
                self._commit_execution()
                return True
            except Exception as e:
                logger.exception(f"[EXCEPTION][INSERT] : Query - {query} - Execution Couldn't Complete Due to Exception : {e}")
                return e

        return Exception("Error Cursor")

    def select(self, query, fetch='all', *args, **kwargs):
        if hasattr(self, "_cursor"):
            logger.exception("[XXXX] C1")
            try:
                logger.exception(f"[XXXX] C3 - {query}")
                self._cursor.execute(query, *args, **kwargs)
                if fetch != 'all':
                    logger.exception("[XXXX] C2")
                    return self._cursor.fetchone()
                else:
                    return self._cursor.fetchall()

            except Exception as e:
                logger.exception(f"[EXCEPTION][SELECT] : Query - {query} - Execution Couldn't Complete Due to Exception : {e}")
                return e
        return Exception("Error Cursor")

    def update(self, query, *args, **kwargs):
        if hasattr(self, "_cursor"):
            try:
                self._cursor.execute(query, *args, **kwargs)
                self._commit_execution()
                return True
            except Exception as e:
                logger.exception(f"[EXCEPTION][UPDATE] : Query - {query} - Execution Couldn't Complete Due to Exception : {e}")
                return e

        return Exception("Error Cursor")

    def delete(self, query, *args, **kwargs):
        if hasattr(self, "_cursor"):
            try:
                self._cursor.execute(query, *args, **kwargs)
                self._commit_execution()
                return True
            except Exception as e:
                logger.exception(f"[EXCEPTION][DELETE] : Query - {query} - Execution Couldn't Complete Due to Exception : {e}")
                return e

        return Exception("Error Cursor")
