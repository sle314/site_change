# -*- coding: utf-8 -*-
import sys
import urllib2
import time
import smtplib
import requests
from email.mime.text import MIMEText


class Mailer(object):
    def __init__(self, config):
        self.config = config
        self.server = None

    def open_connection(self):
        try:
            self.server = smtplib.SMTP(self.config['SERVER'])
            self.server.ehlo()
            self.server.starttls()
            self.server.login(self.config['USERNAME'], self.config['PASSWORD'])
        except Exception as e:
            self.server = None
            raise Exception("Couldn't connect to mail server. Wrong username/password?")

    def close_connection(self):
        if self.server is not None:
            try:
                self.server.quit()
            except Exception as e:
                print e
        self.server = None

    def connect(self):
        try:
            self.open_connection()
        except Exception as e:
            print e

    def disconnect(self):
        self.close_connection()

    def send_mail(self, from_name, subject, message):
        if self.server is not None:
            msg = MIMEText(message, 'html', 'utf-8')
            msg['From'] = '%s <%s>' % (from_name, self.config['FROM'])
            msg['To'] = ",".join(self.config['TO'])
            msg['Subject'] = subject
            try:
                self.server.sendmail(self.config['FROM'], self.config['TO'], msg.as_string())
            except Exception as e:
                self.server = None
                print e

    def send(self, from_name, subject, message):
        self.connect()
        self.send_mail(from_name, subject, message)
        self.disconnect()


class Smser(object):
    def __init__(self, config):
        self.config = config

    def send_sms(self, message):
        for number in self.config['NUMBERS']:
            payload = {'number': number, 'message': "%s" % message}
            requests.post(self.config['API'], data=payload)


class Notifier(object):
    def __init__(self, mailer, smser, duration):
        self.mailer = mailer
        self.smser = smser
        self.duration = duration

    def send_sms(self, message):
        if self.smser is not None:
            self.smser.send_sms(message)

    def send_mail(self, message):
        if self.mailer is not None:
            self.mailer.send('Site Change', 'Site Change', message)

    def sound_alert(self):
        i = 0
        while i < self.duration:
            i += 1
            sys.stdout.write('\a')
            sys.stdout.flush()


class SiteChangeHandler(object):
    def __init__(self, url, notifier, delay=2, send_mail=False, send_sms=False, sound_alert=False):
        self.url = url
        self.send_mail = send_mail
        self.send_sms = send_sms
        self.sound_alert = sound_alert
        self.notifier = notifier
        self.delay = delay
        self.html = None
        self.fetch_init_data()

    def fetch_init_data(self):
        i = 0
        while True:
            self.html = self.fetch_data()
            if self.html is not None:
                break
            i += 1
            if i > 1000:
                sys.exit(0)
            time.sleep(2)
        print "Fetched init data!"

    def fetch_data(self):
        try:
            response = urllib2.urlopen(self.url)
            return response.read() if response else None
        except Exception as e:
            print e

        return None

    def handle_change(self):
        if self.notifier:
            if self.send_mail:
                self.notifier.send_mail(self.url)
            if self.send_sms:
                self.notifier.send_sms(self.url)
            if self.sound_alert:
                self.notifier.sound_alert()
        print "Change handled!"

    def start_listening(self, stop_on_change=True):
        "Listening for changes!"
        while True:
            html = self.fetch_data()
            if self.html != html:
                self.html = html
                print "Change occured!"
                self.handle_change()
                if stop_on_change:
                    break

            time.sleep(self.delay)
