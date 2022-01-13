#!/opt/scripts/bin/launch.sh -e huissier 
import datetime
import os
import shutil
import sys
import xml.etree.ElementTree as xmlET
import zipfile

import paramiko
import pyodbc
from identity import *

leroy_folder_root = '/opt/scripts/huissier/tmp/leroy'
modero_folder_root = '/opt/scripts/huissier/tmp/modero'
modero_folder_upload = '/data/modero/ToModero2'
leroy_folder_upload = '/data/leroy/ToLeroy'
sap_folder_root = '/opt/scripts/huissier/tmp/sap'
sap_folder_upload = '/OAA_Bailiff_ESend/Parking'
sap_folder_download = '/OAA_Bailiff_EReceive/Parking'
input_folder = '/opt/scripts/huissier/tmp/InputFiles'



# output_folder = '/opt/scripts/huissier/tmp/output_files'

def connectionSAP(credential):
    try:
        con = credentials[credential]
        transport = paramiko.Transport((con["host"], con["port"]))
        transport.connect(username=con["user"], password=con["pass"])
        return paramiko.SFTPClient.from_transport(transport)
    except Exception as e:
        print(e)
        raise Exception("Connection Crush-ftp failed")



# Chargement des fichiers depuis la source
def downloadXmlFiles():
    try:
        sftp = connectionSAP('sftp')
        for file in sftp.listdir(sap_folder_download):
            sftp.get(os.path.join(sap_folder_download, file), os.path.join(input_folder, file))
            # Enleve le document en crushftp
            sftp.remove(os.path.join(sap_folder_download, file))
    except Exception as e:
        print("An error occured while downloading input files and folders :\n", e)
        raise Exception("Ftp download failed")



def uploadAttributionFile():
    try:
        sftp = connectionSAP('sftp')
        for file in os.listdir(sap_folder_root):
            sftp.put(os.path.join(sap_folder_root, file), os.path.join(sap_folder_upload, file))
    except Exception as e:
        print("An error occured while uploading attribution file :\n", e)
        return False
    return True



def move_files_tmp(location):
    try:
        for ele in os.listdir(location):
            ele_path = os.path.join(location, ele)
            if os.path.isdir(ele_path):
                shutil.rmtree(ele_path, ignore_errors=True)
            else:
                shutil.move(ele_path, '../testfiles/tmp')
    except Exception as e:
        print(e)
        raise Exception("Clear files not succeeded")



def clear_files(location):
    try:
        for ele in os.listdir(location):
            ele_path = os.path.join(location, ele)
            if os.path.isdir(ele_path):
                shutil.rmtree(ele_path, ignore_errors=True)
            else:
                os.remove(ele_path)
    except Exception as e:
        print(e)
        raise Exception("Clear files not succeeded")



def extract_zipped_files(location):
    try:
        for ele in [ele for ele in os.listdir(location) if ele.endswith('zip')]:
            path = os.path.join(location, ele)
            z_file = zipfile.ZipFile(path)
            folder = ele[:-4]
            if not os.path.isdir(os.path.join(location, folder)):
                os.mkdir(os.path.join(location, folder))
                z_file.extractall(os.path.join(location, folder))
            else:
                z_file.extractall(location)
    except Exception as e:
        print(e)
        raise Exception("Extracting zipfiles failed")



def sftpConnector(credential):
    try:
        con = credentials[credential]
        transport = paramiko.Transport((con["host"], con["port"]))
        key = paramiko.RSAKey.from_private_key_file(con["key"])
        transport.connect(username=con["user"], pkey=key)
        return paramiko.SFTPClient.from_transport(transport)
    except Exception as e:
        print(e)
        raise Exception("SFTP Connection failed")



# Charger les photos et les pdf dans le sftp de destination
def uploadFiles():
    try:
        sftp = sftpConnector('sftpOut')
    except Exception as e:
        print("Error uploading files")
        print(e)
        return False

        # Leroy
    try:
        for ele in os.listdir(leroy_folder_root):
            if ele.endswith('zip'):
                sftp.put(os.path.join(leroy_folder_root, ele), os.path.join(leroy_folder_upload, ele))
    except Exception as e:
        print("Error uploading files")
        print(e)
        return False

        # Modero
    try:
        for ele in os.listdir(modero_folder_root):
            if ele.endswith('zip'):
                sftp.put(os.path.join(modero_folder_root, ele), os.path.join(modero_folder_upload, ele))
    except Exception as e:
        print("Error uploading files")
        print(e)
        return False
    return True



def checkAnFormatXmlFileTree(folder, file):
    try:
        formatted_file = open(os.path.join(input_folder, folder, file)).read().replace("/", "</").replace("",
                                                                                                           "").rstrip(
                '\x00')
        return xmlET.ElementTree(xmlET.fromstring(formatted_file))
    except Exception as e:
        print(e)
        raise Exception("Format XML File failed")



def appendToAttributions(root, vcs, bailiff_id):
    dossier = xmlET.SubElement(root, 'Dossier')
    attribution = xmlET.SubElement(dossier, 'AttributionMsg', xmlns="urn:parking.brussels:agencyservice:model:v1")
    xmlET.SubElement(attribution, "OGM", xmlns="").text = vcs
    xmlET.SubElement(attribution, "ID", xmlns="").text = str(bailiff_id)
    # attribution_tree.getroot().append(dossier)



# Injecter les dossiers dans la base de données
def insertCasesToDb(folder, file, attribution_root):
    try:
        tree = checkAnFormatXmlFileTree(folder, file)
        leroy_root = xmlET.Element("Dossiers")
        modero_root = xmlET.Element("Dossiers")
        leroy_tree = xmlET.ElementTree(leroy_root)
        modero_tree = xmlET.ElementTree(modero_root)
        leroy_file = open(os.path.join(leroy_folder_root, folder, file), "wb")
        modero_file = open(os.path.join(modero_folder_root, folder, file), "wb")
        file_root = tree.getroot()
        global vcs_list
        for dossier in file_root.iter('Dossier'):
            code = dossier.find('Mouvement').find('Annulation').find('CodeAnnul').text
            vcs = dossier.find('VCS').text
            if code == 'X':
                if vcs in vcs_list:
                    modero_tree.getroot().append(dossier)
                    appendToAttributions(attribution_root, vcs, 2)
                else:
                    leroy_tree.getroot().append(dossier)
                    appendToAttributions(attribution_root, vcs, 1)
            else:
                modero_tree.getroot().append(dossier)
                appendToAttributions(attribution_root, vcs, 2)
                try:
                    cursor.execute("SELECT count(*) from CASES where VCS = ?", vcs)
                    row = cursor.fetchone()
                    if row[0] == 0:
                        cursor.execute("INSERT INTO dbo.CASES (VCS, Bailiff) VALUES  (?, 1)", vcs)
                except pyodbc.Error as e:
                    print(e)
                vcs_list.append(vcs)
        leroy_tree.write(leroy_file, encoding='utf-8', xml_declaration=True)
        modero_tree.write(modero_file, encoding='utf-8', xml_declaration=True)
        cursor.commit()
        # log_writer.writerow([str(datetime.datetime.now()), folder, file, 'done'])
    except Exception as e:
        print("Inserting data to database from :", file)
        print(e)
        # log_writer.writerow([str(datetime.datetime.now()), folder, file, e])
        raise Exception("Insert into DB failed")



def copyFileToOutputFolder(file_path, dest_path):
    try:
        shutil.copy(file_path, dest_path)
    except Exception as e:
        print(e)
        raise Exception("Write to outputfolder failed")



def processUpdateFile(folder, file):
    try:
        tree = checkAnFormatXmlFileTree(folder, file)
        leroy_root = xmlET.Element("Dossiers")
        modero_root = xmlET.Element("Dossiers")
        leroy_tree = xmlET.ElementTree(leroy_root)
        modero_tree = xmlET.ElementTree(modero_root)
        leroy_file = open(os.path.join(leroy_folder_root, folder, file), "wb")
        modero_file = open(os.path.join(modero_folder_root, folder, file), "wb")
        file_root = tree.getroot()
        global vcs_list
        for dossier in file_root.iter("Dossier"):
            if dossier.find('VCS').text in vcs_list:
                modero_tree.getroot().append(dossier)
            else:
                leroy_tree.getroot().append(dossier)
        leroy_tree.write(leroy_file, encoding='utf-8', xml_declaration=True)
        modero_tree.write(modero_file, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(e)
        raise Exception("Processing update file failed")



def getVcsPictures(vcs):
    try:
        pic_folders = [folder for folder in os.listdir(input_folder) if
                       folder.__contains__('OTH') and not folder.endswith('zip')]
        pictures = []
        for folder in pic_folders:
            files = []
            for file in [file for file in os.listdir(os.path.join(input_folder, folder)) if file.__contains__(vcs)]:
                files.append(file)
            pictures.append({
                    "folder": folder,
                    "files" : files
            })
        return pictures
    except Exception as e:
        print(e)
        raise Exception("Get VCS Pictures failed")



def getVcsPDFs(vcs):
    try:
        pdf_folders = [folder for folder in os.listdir(input_folder) if
                       folder.__contains__('PDF') and not folder.endswith('zip')]
        pdf_files = []
        for folder in pdf_folders:
            files = []
            for file in [file for file in os.listdir(os.path.join(input_folder, folder)) if file.__contains__(vcs)]:
                files.append(file)
            pdf_files.append({
                    "folder": folder,
                    "files" : files
            })
        return pdf_files
    except Exception as e:
        print(e)
        raise Exception("get PDF documents failed")



def processPdfAndPhotos():
    try:
        for folder in os.listdir(leroy_folder_root):
            if not os.path.isdir(os.path.join(leroy_folder_root, folder)):
                print(folder, ' is not a folder')
                continue
            for ele in [ele for ele in os.listdir(os.path.join(leroy_folder_root, folder)) if
                        ele.__contains__('CREATE')]:
                file_tree = xmlET.parse(os.path.join(leroy_folder_root, folder, ele))
                file_root = file_tree.getroot()
                for dossier in file_root:
                    vcs = dossier.find('VCS').text
                    # processing photos
                    pics_data = getVcsPictures(vcs)
                    if len(pics_data) > 0:
                        for ele in pics_data:
                            source_folder = os.path.join(input_folder, ele['folder'])
                            destination_folder = os.path.join(leroy_folder_root, ele['folder'])
                            if not os.path.isdir(destination_folder):
                                os.mkdir(destination_folder)
                            for file in ele['files']:
                                source = os.path.join(source_folder, file)
                                destination = os.path.join(destination_folder, file)
                                shutil.move(source, destination)
                    # processing pdfs
                    pdf_data = getVcsPDFs(vcs)
                    if len(pdf_data) > 0:
                        for ele in pdf_data:
                            source_folder = os.path.join(input_folder, ele['folder'])
                            destination_folder = os.path.join(leroy_folder_root, ele['folder'])
                            if not os.path.isdir(destination_folder):
                                os.mkdir(destination_folder)
                            for file in ele['files']:
                                source = os.path.join(source_folder, file)
                                destination = os.path.join(destination_folder, file)
                                shutil.move(source, destination)
        moveModeroPdfsAndPictures()
    except Exception as e:
        print(e)
        raise Exception("Process PDF and photos failed")



# deplacer les photo et ^df restants chez modero
def moveModeroPdfsAndPictures():
    try:
        for ele in os.listdir(input_folder):
            if os.path.isdir(os.path.join(input_folder, ele)) and (ele.__contains__('OTH') or ele.__contains__('PDF')):
                shutil.move(os.path.join(input_folder, ele), modero_folder_root)
    except Exception as e:
        print(e)
        raise Exception("Move Modero failed")



def processFiles():
    try:
        attribution_root = xmlET.Element("Dossiers")
        attribution_tree = xmlET.ElementTree(attribution_root)
        for folder in [folder for folder in os.listdir(input_folder) if
                       os.path.isdir(os.path.join(input_folder, folder))]:
            create_files = [file for file in os.listdir(os.path.join(input_folder, folder)) if
                            file.__contains__('CREATE')]
            other_files = [file for file in os.listdir(os.path.join(input_folder, folder)) if
                           file.__contains__('AUTRE')]
            if not os.path.isdir(os.path.join(leroy_folder_root, folder)):
                os.mkdir(os.path.join(leroy_folder_root, folder))
            if folder.__contains__('XML') and not os.path.isdir(os.path.join(modero_folder_root, folder)):
                os.mkdir(os.path.join(modero_folder_root, folder))
            for file in create_files:
                insertCasesToDb(folder, file, attribution_root)
            for file in other_files:
                processUpdateFile(folder, file)
        attribution_tree.write(generateAttributionFileName(), encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(e)
        raise Exception("Process files Failed")



def compress_output_files():
    try:
        for folder in [leroy_folder_root, modero_folder_root]:
            for ele in os.listdir(folder):
                if ele.endswith('.zip'):
                    print('Zipfile already exists: ' + ele)
                    continue
                zip_object = zipfile.ZipFile(os.path.join(folder, ele + '.zip'), 'w')
                # zip_object.write(os.path.join(folder,ele))
                for root, dirs, files in os.walk(os.path.join(folder, ele)):
                    for file in files:
                        zip_object.write(os.path.join(root, file),
                                         os.path.relpath(os.path.join(root, file),
                                                         os.path.join(folder, ele)))
                zip_object.close()
    except Exception as e:
        print(e)
        raise Exception("Compressing files failed")



def generateAttributionFileName():
    fileName = "ATTR_{}.xml".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return open(os.path.join(sap_folder_root, fileName), "wb")



# if len(os.listdir(input_folder) or os.listdir(leroy_folder_root) or os.listdir(modero_folder_root) or os.listdir(sap_folder_root)) != 0  :
if len(os.listdir(input_folder) or os.listdir(leroy_folder_root) or os.listdir(modero_folder_root)) != 0:
    print("folders not empty")
    sys.exit(1)

## Main run
try:
    ### Crée la connexion vers la DB de huissier
    conn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server}; Server=SV009; Database=HUISSIER; UID=script_huissier; PWD=WZswlXV7A5B')
    cursor = conn.cursor()

    ### Check all VCS to Modero
    vcs_list = [row[0] for row in cursor.execute("SELECT VCS FROM CASES").fetchall()]
    # log = open("/opt/scripts/huissier/log.csv", 'a', encoding="utf-8", newline="")
    # log_writer = csv.writer(log)

    downloadXmlFiles()  # Telechargement et extraction des fichiers téléchargés
    extract_zipped_files(input_folder)

    processFiles()  # d'abord exécuter les create (insertion dans la db et envoi vers modero)
    processPdfAndPhotos()  # Deplacer les photos et les pdf vers le bon huissier

    compress_output_files()
    if uploadFiles():
        clear_files(input_folder)  # Nettoyer le dossier des entrants
        clear_files(leroy_folder_root)  # Nettoyer le dossier leroy
        clear_files(modero_folder_root)  # Nettoyer le dossier modero

    # Chargement des fichiers vers les sftp de destination

    if uploadAttributionFile():  # chargement du fichier d'attribution vers SAP
        move_files_tmp(sap_folder_root)  # Nettoyer le dossier sap en envoyer les vers /tmp
        # clear_files(sap_folder_root)#Nettoyer le dossier sap

except Exception as e:
    print(e)

open()