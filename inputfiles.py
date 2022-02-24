import os
import zipfile

from attributionfile import AttributionFile
from createfile import CreateFile
from sshConnection import SSHConnection



class InputFiles:
    """
    Class representing all input file for the bailiff

    """
    remote_directory: str = None
    local_directory: str = None
    files = []
    vcs_list = None


    def __init__(self, _remote_directory, _local_directory, _vcs_list):
        """Return an object to hold the files

        :param _remote_directory :
            Directory where the files are stored on sap
        :param _local_directory :
            Directory where the input files will be kept during processing
        """
        self.remote_directory = _remote_directory
        self.local_directory = _local_directory
        self.vcs_list = _vcs_list


    def getInput(self):
        """ Get all the files from the SAP site and unpack them in a directory each

        :raises Exception in case not all files are extracted

        :returns itself
        """
        self.getFilesFromSAP()
        self.unpackFiles()
        return self


    def getFilesFromSAP(self):
        """Download all files from SAP

        :returns itself
        """

        # Open connection
        conn = SSHConnection("sap").open()

        # Download all files and remove them from sap
        conn.getFiles(self.remote_directory, self.local_directory, False)
        return self


    def unpackFiles(self):
        """
        Unzip all the files in de local_directory and add them to the files list

        :raises Exception in case not all files are extracted

        :return Itself
        """
        # for all zip files in local_directory
        _zipFileList = [_f for _f in os.listdir(self.local_directory) if _f.endswith('.zip')]
        for _zipFileName in _zipFileList:
            ''' extract a directory per zipfile is made to put all files '''
            # define the directory name as the name of zip-file without the extension
            _zipFileDir = os.path.join(self.local_directory, _zipFileName.rsplit('.', 1)[0])
            # Extract zipfile into zipFileDir
            _zipfile = zipfile.ZipFile(os.path.join(self.local_directory, _zipFileName))
            _zipfile.extractall(_zipFileDir)
            # Add list of files to the variable files
            for _fileName in _zipfile.namelist():
                self.files += os.path.join(_zipFileDir, _fileName)

        # Check if all files are extracted
        for _f in [_f for _f in self.files if os.path.isfile(os.path.join(self.local_directory, _f))]:
            raise Exception("""Files not well unzipped, check for file {_f}""")

        return self


    def process(self, _conf):
        """Check each XML file and split them over the 2 bailiffs

        For each XML file take the retributions out and check if the retribution is already given to Leroy.
        In that case attribute the retribution to Leroy otherwise to Modero.

        After added the xml for the retribution to the new file, the output files for the retribution will be added to the directory
        """
        # Get all extracted directories starting with outputXML1 (normal format is outputXML1_yyyymmddhhmmss)
        _directories = [_d for _d in os.listdir(self.local_directory)
                        if (os.path.isdir(os.path.join(self.local_directory, _d)) and
                            _d.startswith('outputXML1'))]

        # for each directory found, find the XML files
        for _dir in _directories:
            _inputDir = os.path.join(self.local_directory, _dir)
            _inputFiles = [_f for _f in os.listdir(_inputDir)
                           if _f.endswith('.xml')]

            # if no files found, continue with next directory
            if _inputFiles is None:
                continue

            # Create attribution file
            _attrFileName = "ATTR_" + _dir.rsplit("_", 1)[1]
            _attrFile = AttributionFile(_attrFileName)

            # process each XML file found
            for _file in _inputFiles:
                createFile = CreateFile(_file, _inputDir, _attrFile, self.vcs_list)
                createFile.process()
                createFile.save()

            # After processing all XML files save attribution file
            _attrFile.Save()

        return self


    def upload(self, _conf):
        """Upload the result files to the places

        Leroy, Modero files =>  to the sv002

        Attribution files => to SAP directly
        """

        for _party in _conf["upload"].keys():
            # Open connection
            if _party == "sap":
                _connectionString = "sap"
                # Only xml files uploaded
                _extension = "xml"
            else:
                _connectionString = "sftpOut"
                # Only zip files uploaded
                _extension = "zip"
            conn = SSHConnection(_connectionString).open()

            # upload all files
            conn.putFiles(_conf["root"][_party], _conf["upload"][_party], _extension)

        return self

    def pack(self, _conf):
        """Zip the result files to the places

        Leroy, Modero files =>  zip per directory

        Attribution files => no zipping needed
        """
        # zip all directories to files except for SAP and Input
        for _party in [_p for _p in _conf["upload"].keys()
                       if (_p != "sap" and _p != "input")]:

            # check all directories in the directory of the party
            _directories = [_d for _d in os.listdir(_conf["root"][_party])
                            if os.path.isdir(os.path.join(_conf["root"][_party], _d))]

            # zip each directory
            for _dir in _directories:
                _directory = os.path.join(_conf["root"][_party], _dir)
                _zipFileName = _directory + ".zip"
                _zipfile = zipfile.ZipFile(_zipFileName, mode="x")
                # put each file in de archive
                for _file in os.listdir(_directory):
                    _zipfile.write(os.path.join(_directory, _file), _file)
                _zipfile.close()

        return self
