import unittest

from sshConnection import SSHConnection


class MyTestCase(unittest.TestCase):

    def test_OpenSSHConnection(self):
        conn = SSHConnection("testSSH").open()
        self.assertTrue(conn.isActive(), "Connection not open")
        conn.close()

    def test_putFile(self):
        conn = SSHConnection("testSSH").open()
        conn.putFiles("c:/users/kcox/PycharmProject/")

if __name__ == '__main__':
    unittest.main()
