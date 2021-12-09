import os


class input_file:
    """
    Class representing all input file for the bailiff
    """
    leroy_folder_root = '/opt/scripts/huissier/tmp/leroy'
    modero_folder_root = '/opt/scripts/huissier/tmp/modero'
    modero_folder_upload = '/data/modero/ToModero2'
    leroy_folder_upload = '/data/leroy/ToLeroy'
    sap_folder_root = '/opt/scripts/huissier/tmp/sap'
    sap_folder_upload = '/OAA_Bailiff_ESend/Parking'
    sap_folder_download = '/OAA_Bailiff_EReceive/Parking'
    input_folder = '/opt/scripts/huissier/tmp/input_files'

    # output_folder = '/opt/scripts/huissier/tmp/output_files'

    def __init__(self):
        return self

    def getInput(self):
        if not self.directoriesEmpty():
            raise Exception("ERROR: input directories not empty, last run failed?")

        self.getFilesFromSAP()
        self.unpackFiles()
        return self

    def directoriesEmpty(self):
        if len(os.listdir(self.input_folder)
               or os.listdir(self.leroy_folder_root)
               or os.listdir(self.modero_folder_root)
               or os.listdir(self.sap_folder_root)
               ) != 0:
            return False
        else:
            return True

    def getFilesFromSAP(self):

        pass
