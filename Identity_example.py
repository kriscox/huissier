credentials = {
    "sap": {
        "host": "cftp.sec.brussels",
        "port": 2222,
        "user": "***",
        "pass": "***"
    },
    "sftpOut": {
        "host": "SV002",
        "port": 22,
        "user": "***",
        "key": "***"
    },
    "sqlserver": {
        "Driver": "ODBC Driver 17 for SQL Server",
        "Server": "sv009",
        "Uid": "***",
        "Pwd": "***"
    }
}


def config_access(access_id):
    for key, value in access_id.items():
        for entry in credentials[key].keys():
            value[entry] = credentials[key][entry]

    return access_id
