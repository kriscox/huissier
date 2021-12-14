import os
import unittest

from sshConnection import SSHConnection


class sshConnectionCase(unittest.TestCase):
    testdirBase = "c:/Users/kcox/PycharmProjects/bailif/testfiles/"
    testdir= os.path.join(testdirBase, "testresources")
    testdirtmp = os.path.join(testdirBase, "testfiles/tmp")
    testFile1 = "testfile1.txt"

    def setUp(self) -> None:
        self.conn = SSHConnection("testSSH").open()
        if not os.path.isdir(self.testdir):
            os.mkdir(self.testdir)
        if not os.path.isdir(self.testdirtmp):
            os.mkdir(self.testdirtmp)
        _files = os.listdir(self.testdirtmp)
        if _files:
            for _file in _files:
                os.remove(os.path.join("/", self.testdirtmp, _file))

    def tearDown(self) -> None:
        _files = os.listdir(self.testdirtmp)
        if _files:
            for _file in _files:
                os.remove(os.path.join("/", self.testdirtmp, _file))
        self.conn.close()

    def test_OpenSSHConnection(self):
        self.assertTrue(self.conn.isActive(), "Connection not open")
        self.conn.close()

    def test_putFile(self):
        self.conn.putFiles(self.testdir, "/tmp/testdir", "txt")
        self.conn.getFiles("/tmp/testdir", self.testdirtmp)
        self.assertTrue(self.testFile1 in os.listdir(self.testdir),
                        "File not uploaded")


if __name__ == '__main__':
    unittest.main()
