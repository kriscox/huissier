from SqlConnection import SQLConnection

DBConn: SQLConnection = SQLConnection()



class VcsList:
    List = []


    def __init__(self):
        pass

    def __contains__(self, item: str):
        for _item in self.List:
            if _item == item:
                return True
        DBConn.Execute(f"""SELECT VCS FROM HUISSIER.dbo.CASES WHERE VCS = '{item}'""")
        return DBConn.Next() is not None


    def __add__(self, item: str):
        self.List.append(item)
        return self


    def save(self):
        for item in self.List:
            DBConn.Execute(f"""INSERT INTO HUISSIER.dbo.CASES VALUES('{item}', 1)""")
        return self


    def __delete__(self, instance):
        self.save()
        return self
