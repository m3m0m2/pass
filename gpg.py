from subprocess import *
"""
python gnupg seems to have a bug that doesn't recognize new gpg statuses,
calling gpg externally is more reliable
"""


class Gpg:
  def __init__(self, user, passwd):
    self.user = user
    self.passwd = passwd

  def encrypt(self, text):
    cmd = ['gpg', '--armor', '--encrypt', '--recipient']
    cmd.append(self.user)
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)
    pipe.stdin.write(text)
    return pipe.communicate()[0]

  def decrypt(self, text):
    cmd = ['gpg', '--decrypt', '--quiet', '--batch', '--pinentry-mode', 'loopback', '--passphrase']
    cmd.append(self.passwd)
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)
    pipe.stdin.write(text)
    return pipe.communicate()[0]


