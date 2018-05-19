#!/usr/bin/python

import argparse
import config
from gs.gs import *
from gs.ss import *
from gpg import Gpg
from oauth2client import tools
import re
import os
import os.path
import getpass


def out(text):
  print("%s" % (text,))


class Pass:
  def __init__(self, args):
    self.args = args
    self.SPREADSHEET_ID = args.sid
    self.SPREADSHEET_TAB = args.tab
    self.service = None
    self.sheet = None
    self.gpg = Gpg(config.gpg_user, config.gpg_passwd)
    self.csv_sep = "\t"
    self.dir = os.path.dirname(__file__)

  # lazy call when needed
  def getSheet(self):
    if self.sheet is None:
      self.service = GoogleService('Password Manager', self.dir, self.args).get_service()
      self.sheet = GSheet(self.service, self.SPREADSHEET_ID)
    return self.sheet

  def getPasswdFile(self):
    return os.path.join(self.dir, config.passwd_file)

  def syncUp(self):
    passwd_file = self.getPasswdFile()
    if not os.path.isfile(passwd_file):
      out("Error: cannot open file %s" % passwd_file)
      return
    sarea = SSArea(4,0,self.csv_sep)
    sarea.loadCsv(passwd_file)
    self.getSheet().setValues(self.grange(),sarea)
    return sarea

  def syncDown(self):
    sarea = self.getSheet().getValues(self.grange())
    sarea.setDelimiter(self.csv_sep)
    self.savePasswd(sarea)
    return sarea

  def savePasswd(self, sarea):
    passwd_file = self.getPasswdFile()
    sarea.writeCsv(passwd_file)

  def loadPasswd(self):
    # TODO: check date of latest update and syncDown
    passwd_file = self.getPasswdFile()
    if not os.path.isfile(passwd_file):
      sarea = self.syncDown()
    else:
      sarea = SSArea(4,0,self.csv_sep)
      sarea.loadCsv(passwd_file)
    return sarea
  
  def grange(self):
    # 'Sheet1!A2:D'
    return GRange(self.SPREADSHEET_TAB, 0, 1, 3).name()


  def search(self, reg0=None, reg1=None, reg3=None):
    tab="\t"
    sarea = self.loadPasswd()

    if sarea.rows == 0:
      out('No data found.')
      return

    header = ['Site', 'User']
    if self.args.decrypt:
      header.append('Password')
    header.append('Note')

    out("%s" % (tab.join(header),))
    for row in sarea:
      if len(row[0]) == 0:
        continue
      if reg0 is not None:
        m = re.search(reg0, row[0])
        if not m:
          continue
      if reg1 is not None:
        m = re.search(reg1, row[1])
        if not m:
          continue
      if reg3 is not None:
        m = re.search(reg3, row[3])
        if not m:
          continue

      show = [row[0], row[1]]
      if self.args.decrypt:
        passwd = row[2].decode('string_escape')
        passwd = self.gpg.decrypt(passwd)
        show.append(passwd)
      show.append(row[3])
      out("%s" % (tab.join(show),))

  def update(self):
    updating = False
    site = self.args.update[0]
    user = self.args.update[1]
    passwd = getpass.getpass()
    passwd = self.gpg.encrypt(passwd)
    passwd = passwd.encode('string_escape')
    note = raw_input('Notes: ')
    save = raw_input('Save? [y/n]: ')
    if not save.lower() == 'y':
      return
    if len(site) == 0:
      out('Error: empty site')
      return

    sarea = self.syncDown()
    for row in sarea:
      if row[0] == site:
        row[0] = site
        row[1] = user
        row[2] = passwd
        row[3] = note
        updating = True
        break
    if not updating:
      sarea.addRow([site, user, passwd, note])

    self.savePasswd(sarea)
    self.syncUp()

  def run(self):
    somethingDone = False

    # These options can perform before others
    if self.args.up_sync:
      self.syncUp()
      somethingDone = True
    elif self.args.down_sync:
      self.syncDown()
      somethingDone = True

    if self.args.find_site or self.args.find_user or self.args.find_note:
      self.search(self.args.find_site, self.args.find_user, self.args.find_note)
    elif self.args.list:
      self.search()
    elif self.args.update:
      self.update()
    else:
      return somethingDone
    return True



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Password Manager using Google Spreadsheet.', parents=[tools.argparser])
    parser.add_argument('-sid', nargs='?', default=config.spreadsheet_id, help='spreadsheet id')
    parser.add_argument('-tab', nargs='?', default=config.spreadsheet_tab, help='spreadsheet tab')
    parser.add_argument('-l', '--list', action='store_true', default=False, help='list')
    parser.add_argument('-fs', '--find-site', nargs='?', default=None, help='search by site')
    parser.add_argument('-fu', '--find-user', nargs='?', default=None, help='search by user')
    parser.add_argument('-fn', '--find-note', nargs='?', default=None, help='search by note')
    parser.add_argument('-u', '--update', nargs=2, default=None, help='update: <site> <user>')
    parser.add_argument('-d', '--decrypt', action='store_true', default=False, help='decrypt')
    parser.add_argument('-ds', '--down-sync', action='store_true', default=False, help='down sync')
    parser.add_argument('-us', '--up-sync', action='store_true', default=False, help='up sync')

    args = parser.parse_args()

    p = Pass(args)
    if not p.run():
      parser.parse_args(['-h'])
