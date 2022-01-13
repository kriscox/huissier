import os
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring
import xml.etree.ElementTree

import myconfig



class AttributionFile:
    directory = myconfig.MyConfig()["root"]["sap"]
    attrRoot: Element
    attrTree: ElementTree
    filename = None
    dirty: bool = False


    def __init__(self, _filename):
        """Creates a new attribution file and builds a basic structure

        Saves the file in the correct directory afterwards to be uploaded to SAP

        :param _filename: desired name of te attribution file
        :type _filename:
        """
        self.filename = _filename + ".xml"
        self.attrRoot = Element("Dossiers")
        self.attrTree = ElementTree(self.attrRoot)
        pass


    def Add(self, _vcs, _bailiff):
        """Add the dossier number to the attribution xml file and attribute it to a bailiff

        _bailiff is a number 1 is Leroy and 2 is Modero

        :param _vcs: Identification number of the dossier
        :type _vcs:
        :param _bailiff: number representing the bailiff (1: Leroy, 2: Modero)
        :type _bailiff:
        """
        self.dirty = True
        _dossierElement = SubElement(self.attrRoot, "Dossier")
        _attributionElement = SubElement(_dossierElement,
                                         "AttributionMsg",
                                         xmlns="urn:parking.brussels:agencyservice:model:v1")
        SubElement(_attributionElement,
                   "OGM",
                   xmlns="").text = _vcs
        SubElement(_attributionElement,
                   "ID",
                   xmlns="").text = str(_bailiff)
        return self


    def Save(self):
        """Save the attribution xml tree to the filename given at creation of the class

        The directory where the file is created will be found in the config file under root -> sap

        :rtype: object
        """
        if self.dirty:
            _fileIO = open(os.path.join(self.directory, self.filename), 'wb')
            self.attrTree.write(_fileIO, encoding='utf-8', xml_declaration=True)
        self.dirty = False


    def __del__(self):
        """Save the file on deletion of the object.

        Function executed at the
        """
        self.Save()
