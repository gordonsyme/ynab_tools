#!/usr/bin/python

# Hacky script to convert AIB iBusiness Banking CSV files into a suitable CSV
# for import to YNAB

import sys
import csv
import logging


def main(input, output):
    in_lines = input.readlines()

    assert in_lines[0].startswith("01,"), "AIB transaction CSVs should start with a row tagged \"01\", got: {}".format(in_lines[0])
    assert in_lines[-1] == "99,End of File", "AIB transaction CSVs should end with a row tagged \"99,End of File\", got: {}".format(in_lines[-1])

    in_data = ["Code,Date,Empty1,Details,Currency,Debit,Credit,Balance,Empty2,Empty3,Balance"] + in_lines[1:-1]
    in_csv = csv.DictReader(in_data)

    fields = ('Date', 'Check#', 'Payee', 'Memo', 'Amount')
    out_csv = csv.DictWriter(output, fields)

    header = {}
    for field in fields:
        header[field] = field
    out_csv.writerow(header)

    for row in in_csv:
        logging.debug("Row is: %s" % row)
        if row['Details']:
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
