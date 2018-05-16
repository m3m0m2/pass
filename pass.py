import argparse
import config
from gs.gs import *
from gs.ss import *


def run(args):
  g = GoogleService('Password Manager', None)
  g.get_credentials()
  service = g.get_service()

  # Call the Sheets API
  SPREADSHEET_ID = args.sid
  RANGE_NAME = 'Sheet1!A2:D'
  result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME).execute()
  values = result.get('values', [])
  if not values:
    print('No data found.')
  else:
    for row in values:
        print('%s, %s' % (row[0], row[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Password Manager using Google Spreadsheet.')

    parser.add_argument('list', nargs='?', help='list keys')
    parser.add_argument('sid', nargs='?', default=config.spreadsheet_id, help='spreadsheet id')

    args = parser.parse_args()
    run(args)
