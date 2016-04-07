# -*- coding: utf-8 -*-
import sys
import argparse
import getpass

from models import Mailer, Smser, Notifier, SiteChangeHandler
from config import *


class ArgParser(object):
    @staticmethod
    def get_parser(args):
        args = args
        parser = argparse.ArgumentParser(description='Process some inputs.')

        for key, value in args.iteritems():
            parser.add_argument(*key, **value)
        return parser


class SiteChange(object):
    @staticmethod
    def listen(url, username, server, mail_to, mail_from, send_mail, send_sms, sound_alert,
                    sms_api, numbers, delay):
        if not (sound_alert or send_mail or send_sms):
            send_mail = True

        mailer = None
        if send_mail:
            if '@gmail.com' not in username:
                username = "%s@gmail.com" % username

            password = getpass.getpass('Password for %s: ' % username)
            mailer = Mailer({
                'SERVER': server,
                'TO': mail_to,
                'FROM': mail_from,
                'USERNAME': username,
                'PASSWORD': password
            })
            try:
                mailer.open_connection()
            except Exception as e:
                print e
                sys.exit(0)

        smser = None
        if send_sms:
            smser = Smser({
                'API': sms_api,
                'NUMBERS': numbers
            })

        notifier = Notifier(mailer, smser)

        sc = SiteChangeHandler(
            url,
            notifier,
            delay=delay,
            send_mail=send_mail,
            send_sms=send_sms,
            sound_alert=sound_alert
        )
        try:
            sc.start_listening()
        except KeyboardInterrupt as e:
            print "Stopped!"


if __name__ == "__main__":
    def get_args():
        args = {
            ('-u', '--username'): {
                'default': DEFAULT_USERNAME,
                'dest': 'username',
                'type': str,
                'help': 'account for the smtp server from which the email will be sent'
            },
            ('-url', '--url'): {
                'default': DEFAULT_URL,
                'dest': 'url',
                'type': str,
                'help': 'url to listen to'
            },
            ('-mail', '--mail'): {
                'default': False,
                'action': 'store_true',
                'dest': 'send_mail',
                'help': 'turn on email notification on change (turned on if sms and sound aren\'t)'
            },
            ('-sms', '--sms'): {
                'default': False,
                'action': 'store_true',
                'dest': 'send_sms',
                'help': 'turn on sms notification on change'
            },
            ('-sound', '--sound'): {
                'default': False,
                'action': 'store_true',
                'dest': 'sound_alert',
                'help': 'turn on sound notification on change'
            },
            ('-n', '--numbers'): {
                'default': DEFAULT_NUMBERS,
                'dest': 'numbers',
                'nargs': '*',
                'help': 'numbers to receive sms notification'
            },
            ('-s', '--server'): {
                'default': DEFAULT_SERVER,
                'dest': 'server',
                'type': str,
                'help': 'smtp server'
            },
            ('-sms_api', '--sms_api'): {
                'default': DEFAULT_SMS_API,
                'dest': 'sms_api',
                'type': str,
                'help': 'sms api address'
            },
            ('-mt', '--mail_to'): {
                'default': DEFAULT_MAIL_TO,
                'dest': 'mail_to',
                'nargs': '*',
                'help': 'recipients of email notification'
            },
            ('-mf', '--mail_from'): {
                'default': DEFAULT_MAIL_FROM,
                'dest': 'mail_from',
                'help': 'email address from which the email will be sent'
            },
            ('-d', '--delay'): {
                'default': DEFAULT_DELAY,
                'dest': 'delay',
                'type': int,
                'help': 'delay between change checks'
            }
        }

        parser = ArgParser.get_parser(args)
        return parser.parse_args()

    args = get_args()
    print args
    SiteChange.listen(args.url, args.username, args.server, args.mail_to, args.mail_from,
        args.send_mail, args.send_sms, args.sound_alert, args.sms_api, args.numbers, args.delay)
