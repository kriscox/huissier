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
    dateString = None  # YYYYMMDDhhmmss
    vcs_list = None
    attrFile: AttributionFile = None
    conf = myconfig.MyConfig()
    moderoTree = None
    moderoRoot = None
    leroyTree = None
    leroyRoot = None
    moderoDirty = False
    leroyDirty = False
    initial = True


    def __init__(self, _file, _inputDir, _attrFile: AttributionFile, _vcs_list):
        """Create an object representing the XML content of the file _file in directory _inputDir

                    :param _file: file containing the XML tree
                    :type _file:
                    :param _inputDir: full path of the directory containing the file _file
                    :type _inputDir:
                    :param _attrFile: attribution file object of current attribution
                    :type _attrFile:
                    """
        self.vcs_list = _vcs_list
        self.filename = os.path.join(_inputDir, _file)
        self.directory = _inputDir
        _fileIO = open(self.filename, "r", encoding="utf8")
        self.readFile(_fileIO)
        _fileIO.close()
        self.attrFile = _attrFile
        self.dateString = self.directory.rsplit("_", 1)[1]  # YYYYMMDDhhmmss
        self.moderoTree = xmlET.ElementTree(xmlET.Element("Dossiers"))
        self.moderoRoot = self.moderoTree.getroot()
        self.leroyTree = xmlET.ElementTree(xmlET.Element("Dossiers"))
        self.leroyRoot = self.leroyTree.getroot()
        if ('AUTRE' in _file):
            self.initial = False


    def process(self):
        """Treat all dossiers from the file and create the new files with the corresponding documents

        Meanwhile, build up the corresponding attribution file

        """
        # Process each retribution (XML element named Dossier)
        if not (self.xmlTree.getroot()):
            return self
        for _dossier in self.xmlTree.getroot().iter('Dossier'):
            _vcs = _dossier.find('VCS').text
            # If the dossier is an annulation or an update, then check for which bailiff and add.
            if (not self.initial or
                    (_dossier.find("Mouvement/Annulation/CodeAnnul") is not None and
                     _dossier.find("Mouvement/Annulation/CodeAnnul").text == 'X')):
                if _vcs in self.vcs_list:
                    self.addDossier("modero", _dossier)
                    self.initial and self.attrFile.Add(_vcs, 2)
                else:
                    self.addDossier("leroy", _dossier)
                    self.initial and self.attrFile.Add(_vcs, 1)
            # New dossier is sent to modero and added to the list
            else:
                self.addDossier("modero", _dossier)
                self.attrFile.Add(_vcs, 2)
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
        if _contentFile != '':
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
            self.moderoDirty = True
        elif _bailiff == "leroy":
            self.leroyRoot.append(_dossier)
            self.leroyDirty = True
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
            if not (os.path.isdir(_sourceDirectory)):
                break
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
        # Write XML for Modero
        if self.moderoDirty:
            _moderoDirectoryName = os.path.join(self.conf["root"]["modero"], _directoryName)
            if not (os.path.exists(_moderoDirectoryName)):
                os.mkdir(_moderoDirectoryName)
            _fileIOModero = open(os.path.join(_moderoDirectoryName, os.path.basename(self.filename)), "wb")
            self.moderoTree.write(_fileIOModero, encoding='utf-8', xml_declaration=True)
            self.moderoDirty = False
        # Write XML for Leroy
        if self.leroyDirty:
            _leroyDirectoryName = os.path.join(self.conf["root"]["leroy"], _directoryName)
            if not (os.path.exists(_leroyDirectoryName)):
                os.mkdir(_leroyDirectoryName)
            _fileIOLeroy = open(os.path.join(_leroyDirectoryName, os.path.basename(self.filename)), "wb")
            self.leroyTree.write(_fileIOLeroy, encoding='utf-8', xml_declaration=True)
            self.leroyDirty = False


    def __del__(self):
        self.save()
