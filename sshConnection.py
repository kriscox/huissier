import os

import paramiko

import Identity


class SSHConnection:

    conn: paramiko.transport = None
    sftp: paramiko.SFTPClient
    ssh: paramiko.SSHClient
    config = None

    def __init__(self, _config: str):
        """ Creator class of the SSH transport object, without already opening the connection to the server

        :param _config:
            _config is the name of the connection to be found in the Identity.py file
        """
        # Read configuration in config from Identity file
        _target = {
            f"""{_config}""": {}
        }
        Identity.config_access(_target)
        self.config = _target[_config]

    def open(self):
        """ Opens the connection to the SSH server

        :return:
            itself
        """
        # Open connection
        self.conn = paramiko.Transport((self.config["host"], self.config["port"]))
        if "key" in self.config.keys():
            keyfile = paramiko.RSAKey.from_private_key_file(self.config["key"])
            self.conn.connect(username=self.config["user"], pkey=keyfile)
        else:
            self.conn.connect(username=self.config["user"], password=self.config["pass"])
        if not self.isActive():
            return None
        else:
            self.sftp = paramiko.SFTPClient.from_transport(self.conn)
            return self

    def isActive(self):
        """ Checks if the connection is active, not if the CLIENT(protocol) is active

        :return:
            returns true if the connection is active
        """
        return self.conn.is_active()

    def getFiles(self, _source_path: str, _destination_path: str):
        """ Retrieves all files on the SSH server and puts then in the given path. After each download it removes
        the original file on the server side

        :rtype: sshConnection
        :param _source_path:
            path on SFTP server
        :param _destination_path:
            path on local server
        """
        for _file in self.sftp.listdir(_source_path):
            self.sftp.get(os.path.join(_source_path, _file), os.path.join(_destination_path, _file))
            if os.path.exists(os.path.join(_destination_path, _file)):
                # remove the downloaded files
                self.sftp.remove(os.path.join(_source_path, _file))
            else:
                raise Exception("ERROR: File not correctly downloaded")
        return self