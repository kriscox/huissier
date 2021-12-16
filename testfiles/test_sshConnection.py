import os
import unittest

from sshConnection import SSHConnection



class SshConnectionCase(unittest.TestCase):
    testDirBase = "c:/Users/kcox/PycharmProjects/bailif/testfiles/"
    testDir = os.path.join(testDirBase, "testresources")
    testDirTmp = os.path.join(testDirBase, "testfiles/tmp")
    testFile1 = "testfile1.txt"


    def setUp(self) -> None:
        self.conn = SSHConnection("testSSH").open()
        if not os.path.isdir(self.testDir):
            os.mkdir(self.testDir)
        if not os.path.isdir(self.testDirTmp):
            os.mkdir(self.testDirTmp)
        _files = os.listdir(self.testDirTmp)
        if _files:
            for _file in _files:
                os.remove(os.path.join(self.testDirTmp, _file))


    def tearDown(self) -> None:
        _files = os.listdir(self.testDirTmp)
        if _files:
            for _file in _files:
                os.remove(os.path.join(self.testDirTmp, _file))
        self.conn.close()


    def test_OpenSSHConnection(self):
        self.assertTrue(self.conn.isActive(), "Connection not open")
        self.conn.close()


    def test_putFile(self):
        self.conn.putFiles(self.testDir, "/tmp/testdir", "txt")
        self.conn.getFiles("/tmp/testdir", self.testDirTmp)
        self.assertTrue(self.testFile1 in os.listdir(self.testDir),
                        "File not uploaded")



if __name__ == '__main__':
    unittest.main()
