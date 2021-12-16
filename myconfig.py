myconfig = {
    "root": {
        "leroy": r'C:\Users\kcox\huissier\leroy',
        "modero": r'C:\Users\kcox\huissier\modero',
        "sap": r'C:\Users\kcox\huissier\sap',
        "input": r'C:\Users\kcox\huissier\input'
    },
    "upload": {
        "leroy": "/tmp/leroy/",
        "modero": "/tmp/modero/",
        "sap": "/opt/tmp/sap/upload/"
    },
    "download": {
        "sap": "/opt/tmp/sap/download/"
    }
}


def MyConfig():
    """Return the config elements from myconfig.py

    Structure of the data
    ---------------------
        - root: all local directories [ leroy, modero, sap, output, input ]

        - upload: all directory names to where we need to upload [leroy, modero, sap]

        - download: all directories from which we need to download [sap]

    :return:
        dict with config values
    """
    return myconfig
