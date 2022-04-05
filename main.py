#!/opt/scripts/bin/launch.sh -e huissier 
import os
import shutil

import SqlConnection
import vcs
from inputfiles import InputFiles
from myconfig import MyConfig

SDBConn = SqlConnection.SQLConnection()



def lastRunSuccessful(_directories=None) -> bool:
    """ Check if last run didn't leave files behind

    :param _directories:
        dict of key/values with all local directories as values and the keys as their names
    :return:
        return true in case the last run was successfully cleaned up
    """
    if _directories is not None:
        for _dir in _directories.values():
            if len(os.listdir(_dir)) != 0:
                return False

    return True



def move_files_tmp(_location: str):
    """Move files in directory to /tmp and remove existing directories and the files included in them

    :param _location: Directory to tread
    :type _location: name of the directory
    """
    for _f in os.listdir(_location):
        _file = os.path.join(_location, _f)
        if os.path.isdir(_file):
            shutil.rmtree(_file, ignore_errors=True)
        else:
            if not os.path.exists(os.path.join('/tmp', _f)):
                shutil.move(_file, '/tmp')



def clear_files(_location: str):
    """Remove all files and directories from the location

    :param _location: Directory to clear
    :type _location: name of the directory
    """
    for _f in os.listdir(_location):
        _file = os.path.join(_location, _f)
        if os.path.isdir(_file):
            shutil.rmtree(_file, ignore_errors=True)
        else:
            os.remove(_file)



def cleanUp(_config):
    """Clean up temporary files to be ready for the next run

    The attribution file send to SAP is kept in /tmp for troubleshooting purposes

    :param _config: configuration information about directories
    """
    # copy attribution file to /tmp
    move_files_tmp(_config["root"]["sap"])
    # remove all files in the tmp directories
    for _key in [_key for _key in _config["root"].keys()]:
        clear_files(_config["root"][_key])


########################################################################################################################
#    Main part of the program which gives the actual order of the steps to be taken                                    #
#                                                                                                                      #
#    Actual work is found in classes                                                                                   #
########################################################################################################################
if __name__ == '__main__':
    # read config from file myconfig.py
    config = MyConfig()

    # Create VCS_list
    vcs_list = vcs.VcsList()

    # check if last run did it's cleanup properly
    if not lastRunSuccessful(config["root"]):
        raise Exception("Last run wasn't successful, some files were trailing")

    # Get files from SFTP site and unpack them
    files: InputFiles = InputFiles(config["download"]["sap"], config["root"]["input"], vcs_list)
    files.getInput()

    # Process files
    files.process(config)

    # Zip the files
    files.pack(config)

    # Upload files
    files.upload(config)

    # Add new VCS in database
    vcs_list.save()

    # Clean up temporary files
    cleanUp(config)
