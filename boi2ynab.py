#!/usr/bin/python

# Hacky script to convert Bank Of Ireland TransactionExport.csv files into a
# suitable CSV for import to YNAB

import sys
import csv
import logging


def main(input, output):
    fields = ('Date', 'Check#', 'Payee', 'Memo', 'Amount')

    in_csv = csv.DictReader(input)
    out_csv = csv.DictWriter(output, fields)

    header = {}
    for field in fields:
        header[field] = field
    out_csv.writerow(header)

    for row in in_csv:
        logging.debug("Row is: %s" % row)
        out_row = {}
        out_row['Date'] = row['Date']
        out_row['Payee'] = row['Details']
        if row['Credit']:
            out_row['Amount'] = row['Credit']
        elif row['Debit']:
            out_row['Amount'] = float(row['Debit']) * -1
        else:
            logging.error('Invalid row: %s' % row)
        out_csv.writerow(out_row)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        base_name = sys.argv[1]
        with open(base_name) as inf:
            with open("ynab_%s" % base_name, 'w') as outf:
                main(inf, outf)
    except IndexError:
        print "usage: %s <filename>" % sys.argv[0]
