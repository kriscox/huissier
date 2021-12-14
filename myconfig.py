myconfig = {
    "root": {
        "leroy": "/opt/scripts/huissier/tmp/leroy",
        "modero": "/opt/scripts/huissier/tmp/modero",
        "sap": "/opt/scripts/huissier/tmp/sap",
        #        "output": "/opt/scripts/huissier/tmp/output_files",
        "input": "/opt/scripts/huissier/tmp/input_files"
    },
    "upload": {
        "leroy": "/data/leroy/ToLeroy",
        "modero": "/data/modero/ToModero2",
        "sap": "/OAA_Bailiff_ESend/Parking"
    },
    "download": {
        "sap": "/OAA_Bailiff_EReceive/Parking"
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
