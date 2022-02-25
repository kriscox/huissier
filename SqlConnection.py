import pyodbc
from pandas import read_sql, DataFrame
from pyodbc import Connection

import identity


class SQLConnection:
    data: DataFrame
    conn: Connection
    row: int

    def __init__(self):
        self.row = -1
        target = {
            "sqlserver": {}
        }
        identity.config_access(target)
        try:
            self.conn = pyodbc.connect(
                'Driver={Driver}; Server={Server}; Database={Database}; UID={Uid}; PWD={Pwd}'.format(
                    Driver=target["sqlserver"]["Driver"],
                    Server=target["sqlserver"]["Server"],
                    Database="HUISSIER",
                    Uid=target["sqlserver"]["Uid"],
                    Pwd=target["sqlserver"]["Pwd"]
                )
            )

        except pyodbc.DatabaseError:
            raise Exception("Connection error")

    def Execute(self, query, param=None):
        self.row = 0
        try:
            if param is None:
                self.data = read_sql(query, self.conn)
            else:
                self.data = read_sql(query, self.conn, params=param)

        except pyodbc.DatabaseError as e:
            print(e)
            raise Exception("Query execution error")

    def Execute_No_Result(self, query, param=None):
        self.row = 0
        try:
            if param is None:
                self.data = None
                self.conn.execute(query)
            else:
                self.data = None
                self.conn.execute(query, params=param)

        except pyodbc.DatabaseError as e:
            print(e)
            raise Exception("Query execution error")


    def Next(self):
        if self.data.size <= self.row:
            return None
        rowData = self.data.iloc[self.row]
        self.row += 1
        return rowData

    def ReturnAll(self):
        return self.data

    def Reset(self):
        self.row = 0
