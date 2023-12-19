#!/usr/bin/env python3
import smtplib
from email.message import EmailMessage
import sys
import json
import argparse
import logging

import time

from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_dict(dict):
   return '\n'.join(f'{k}: {v}' for k, v in dict.items())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', default='ihradis', help='Username to log into SMTP server.')
    parser.add_argument('--from-addr', default="ihradis@fit.vutbr.cz", help="Message will be sent from this address (usefull for replies).")
    parser.add_argument('-p', '--password', required=True, help='')
    parser.add_argument('--mail-server', default='smtp.fit.vutbr.cz:465', help='Mail server.')
    parser.add_argument('--subject', default='[semANT] Statistiky Vaseho anotovani', help='Mail subject.')
    parser.add_argument('--template', default='mail_template.txt', help='Mail template.')
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.template) as f:
        template = f.read()

    for line in sys.stdin:
        data = json.loads(line)
        email_address = data['email']
        del data['email']
        #if not ('xbalca11' in email_address or 'ihradis' in email_address):
        #    continue

        msg = EmailMessage()
        msg['Subject'] = args.subject
        msg['From'] = args.from_addr
        msg['To'] = email_address
        #msg['Cc'] = args.login

        data = defaultdict(lambda: '0.00', data)

        msg.set_content(template.format_map(data))

        logging.info(f'EMAIL: {email_address}')
        logging.info(f'DATA: {msg.get_content()}')

        with smtplib.SMTP_SSL(args.mail_server) as s:
            s.login(args.login, args.password)
            s.send_message(msg)
            time.sleep(6)

        logging.info(f'===============================================================================================')
        logging.info(f'===============================================================================================')



if __name__ == '__main__':
    main()