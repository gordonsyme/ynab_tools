import sys
import csv
import re

from bs4 import BeautifulSoup

import logging

logging.basicConfig(level=logging.DEBUG)

fields = ('Date', 'Check#', 'Payee', 'Memo', 'Amount')


def exclusive(a, b):
    return (not a and b) or (not b and a)


def kill_stupid_commas(amount):
    return re.sub(",", "", amount)

def to_text(tag):
    return tag.text.strip()

def fix_money(td):
    return kill_stupid_commas(to_text(td))

def to_row(tr):
    datas = tr.find_all('td')

    date = to_text(datas[0])
    payee = " ".join(to_text(d) for d in datas[1:3]).strip()
    payee = re.sub("\s+", " ", payee)
    debit = fix_money(datas[3])
    credit = fix_money(datas[4])

    if credit:
        amount = credit
    elif debit:
        amount = float(debit) * -1
    else:
        logging.error("Invalid row: {}".format(datas))

    return {'Date': date,
            'Payee': payee,
            'Amount': amount}
            

def foo(cc_html, output):
    soup = BeautifulSoup(cc_html)
    table = soup.find(id='form:transactionDataTable')
    rows = [to_row(tr) for tr in table.tbody.find_all('tr')]

    out_csv = csv.DictWriter(output, fields)
    header = {field:field for field in fields}
    out_csv.writerow(header)

    for row in rows:
        logging.debug("Row is: {}".format(row))
        out_csv.writerow(row)


def main():
    base_name = sys.argv[1]
    csv_name = "ynab_{}".format(re.sub('\.html$', '.csv', base_name))
    with open(base_name) as cc_html:
        with open(csv_name, 'w') as outf:
            foo(cc_html, outf)


if __name__ == '__main__':
    try:
        main()
    except:
        logging.exception("uh oh")
        print "usage: {} <filename>".format(sys.argv[0])
