import SqlConnection

SDBConn = SqlConnection()

if __name__ == '__main__':
    





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
