from SqlConnection import SQLConnection

DBConn: SQLConnection = SQLConnection()



class VcsList:
    List = []
    dirty = False

    def __init__(self):
        pass
        self.dirty = False


    def __contains__(self, item: str):
        for _item in self.List:
            if _item == item:
                return True
        DBConn.Execute(f"""SELECT VCS FROM HUISSIER.dbo.CASES WHERE VCS = '{item}'""")
        return DBConn.Next() is not None


    def __add__(self, item: str):
        if item in self:
            return self
        self.List.append(item)
        self.dirty = True
        return self


    def __set__(self, instance, value):
        self = value
        return self


    def save(self):
        if self.dirty:
            for item in self.List:
                try:
                    DBConn.Execute(f"""INSERT INTO HUISSIER.dbo.CASES VALUES('{item}', 1)""")
                except:
                    print(f"""INSERT INTO HUISSIER.dbo.CASES VALUES('{item}',1)""")
                    raise
        return self


    def __delete__(self, instance):
        self.save()
        return self


    def __del__(self):
        self.save()
