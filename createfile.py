import os
import shutil
import xml.etree.ElementTree as xmlET

import myconfig
import vcs
from attributionfile import AttributionFile



class CreateFile:
    xmlTree = xmlET.ElementTree()
    filename: str = None
    directory = None
    dateString = None  #YYYYMMDDhhmmss
    vcs_list = vcs.VcsList()
    attrFile: AttributionFile = None
    conf = myconfig.MyConfig()
    moderoTree = xmlET.ElementTree(xmlET.Element("Dossiers"))
    moderoRoot = moderoTree.getroot()
    leroyTree = xmlET.ElementTree(xmlET.Element("Dossiers"))
    leroyRoot = leroyTree.getroot()


    def __init__(self, _file, _inputDir, _attrFile: AttributionFile):
        """Create an object representing the XML content of the file _file in directory _inputDir

                    :param _file: file containing the XML tree
                    :type _file:
                    :param _inputDir: full path of the directory containing the file _file
                    :type _inputDir:
                    :param _attrFile: attribution file object of current attribution
                    :type _attrFile:
                    """
        self.filename = os.path.join(_inputDir, _file)
        self.directory = _inputDir
        _fileIO = open(self.filename, "r", encoding="utf8")
        self.readFile(_fileIO)
        _fileIO.close()
        self.attrFile = _attrFile
        self.dateString = self.directory.rsplit("_", 1)[1]  # YYYYMMDDhhmmss


    def process(self):
        """Treat all dossiers from the file and create the new files with the corresponding documents

        Meanwhile, build up the corresponding attribution file

        """
        # Process each retribution (XML element named Dossier)
        for _dossier in self.xmlTree.getroot().iter('Dossier'):
            _vcs = _dossier.find('VCS').text
            # If the dossier is an annulation, then check for which bailiff and add.
            if _dossier.find("Mouvement//Annulation//CodeAnnul") == 'X':
                if _vcs in self.vcs_list:
                    self.addDossier("modero", _dossier)
                    self.attrFile.Add(_dossier, 2)
                else:
                    self.addDossier("leroy", _dossier)
                    self.attrFile.Add(_dossier, 1)
            # New dossier is sent to modero and added to the list
            else:
                self.addDossier("modero", _dossier)
                self.attrFile.Add(_dossier, 2)
                self.vcs_list += _vcs
        return self


    def readFile(self, _FileIO):
        """Read the contents of the file

                    Strip and replace special characters so that is readable for XMLTree
                    """
        _contentFile = _FileIO.read() \
            .replace("/", "</") \
            .replace("", "") \
            .rstrip('\x00')
        self.xmlTree = xmlET.ElementTree(xmlET.fromstring(_contentFile))
        return self


    def addDossier(self, _bailiff, _dossier):
        """Add the dossier xml structure to the corresponding bailiff structure

        Afterwards move also all photo and documents related to the dossier based on vcs to the corresponding output dir

        Important is that in the config the same keys for the bailiff are used in the "root" part of the config

        The documents and photos must be already unpacked in the directories called:
        outputPDF1_YYYYMMDDhhmmss : for the documents
        outputOTH1_YYYYMMDDhhmmss : for the photo's

        :param _bailiff: Name of the bailiff and also the key in the root config
        :type _bailiff:
        :param _dossier: xml-tree of the dossier
        :type _dossier:
        :return: self
        :rtype:
        """
        # Add dossier to bailiff xml tree
        if _bailiff == "modero":
            self.moderoRoot.append(_dossier)
        elif _bailiff == "leroy":
            self.leroyRoot.append(_dossier)
        else:
            raise NotImplementedError("""Bailiff {_bailiff} not implemented yet in createfile.py""")

        ##################
        # Move documents #
        ##################
        # get the retribution number
        _vcs = _dossier.find("VCS").text

        # 2 types of documents in 2 different folders
        #    outputOTH1_YYYYMMDDhhmmss for the photo's
        #    outputPDF1_YYYYMMDDhhmmss for the documents
        # for all the picture in
        for _type in {"outputOTH1_", "outputPDF1_"}:
            _sourceDirectory = os.path.join(self.conf["root"]["input"], _type + self.dateString)
            _destDirectory = os.path.join(self.conf["root"][_bailiff], _type + self.dateString)
            _documents = [_f for _f in os.listdir(_sourceDirectory)
                          if _f.startswith(_vcs)]

            _document: str
            for _document in _documents:
                # Check if the directory in the output directory already exist, if not create it
                if not os.path.isdir(_destDirectory):
                    os.mkdir(_destDirectory)
                shutil.move(os.path.join(_sourceDirectory, _document), _destDirectory)

        return self


    def save(self):
        """
        Save the attribution files in the corresponding directories
        """
        _directoryName = "outputXML1_" + self.dateString
        _fileIOModero = open(os.path.join(self.conf["root"]["modero"], _directoryName, self.filename), "wb")
        self.moderoTree.write(_fileIOModero, encoding='uft-8', xmldeclaration=True)
        _fileIOLeroy = open(os.path.join(self.conf["root"]["leroy"], _directoryName, self.filename), "wb")
        self.leroyTree.write(_fileIOLeroy, encoding='uft-8', xmldeclaration=True)

    def __del__(self):
        self.save()