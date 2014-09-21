# -*- coding: utf-8 -*-
from flask import jsonify
import os, sendgrid

class sendgrid_factory():

    def send_mail(self, subject, html, to, from_, text=None):
        creds = os.getenv('SENDGRID_USERNAME'), os.getenv('SENDGRID_PASSWORD')
        if creds:
            sg = sendgrid.SendGridClient(creds[0], creds[1])
            message = sendgrid.Mail()
            message.add_to(to)
            message.set_subject(subject)
            message.set_from(from_)

            if text:
                message.set_text(text)

            else:
                message.set_html(html)

            status, msg = sg.send(message)
            return jsonify({'message': msg, 'status' : status})
              
        return jsonify({'message':'there was an error', 'status' : 500})