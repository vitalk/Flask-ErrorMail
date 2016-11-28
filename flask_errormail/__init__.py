"""
    flask_errormail
    ~~~~~~~~~~~~~~~

    Flask extension for sending emails to administrators when 500 Internal
    Server Errors occur.

    :copyright: (c) 2012 by Jason Wyatt Feinstein.
    :license: MIT, see LICENSE.txt for more details.

"""
import textwrap
import traceback

from flask import request
from flask import current_app
from flask_mail import Mail
from flask_mail import Message
from werkzeug.local import LocalProxy


_mail = LocalProxy(lambda: current_app.extensions.get('mail'))


default_config = {
    'ERROR_MAIL_SUBJECT': '[Flask|ErrorMail] Exception Detected',
    'ERROR_MAIL_RECIPIENTS': ['admin@example.com'],
    'ERROR_MAIL_SENDER': 'noreply@localhost'
}


class ErrorMail(object):
    '''
    Flask extension for sending emails to administrators when 500 Internal
    Server Errors occur.

    :param app: Flask Application Object
    :type app: flask.Flask
    :param recipients: List of recipient email addresses.
    :type recipients: list or tuple
    :param sender: Email address that should be listed as the sender. Defaults 
        to 'noreply@localhost'
    :type sender: string

    '''
    def __init__(self, app=None, recipients=None, sender='noreply@localhost'):
        if app is not None:
            self.init_app(app, recipients, sender)

    def init_app(self, app, recipients=None, sender='noreply@localhost'):
        mail = app.extensions.get('mail', None)
        if not mail:
            app.logger.warning(
                '`Flask-ErrorMail` extension requires a configured '
                '`Flask-Mail` instance. Ensure the `Flask-Mail` is '
                'configured with current application or unexpected '
                'errors may occur.'
            )

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.register_error_handler(500, self.send_error_mail)

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['error_mail'] = self

    def send_error_mail(self, exception):
        '''Handles the exception message from Flask by sending an email
        to the recipients defined in the application config.
        '''
        _mail.send(
            self.create_error_message(exception)
        )
        return '', 500

    def get_body(self):
        '''Returns a body for an error mail with traceback and
        request info attached.
        '''
        return textwrap.dedent('''
            Traceback:
            {delimiter!s}
            {traceback!s}

            Request Information:
            {delimiter!s}
            {request_info!s}
        ''').format(
            delimiter='='*80,
            traceback=self.get_traceback(),
            request_info=self.get_request_info()
        )

    def create_error_message(self, exception):
        '''Returns a ~`flask_mail.Message` instance with technical info
        about exception which occurs.
        '''
        return Message(
            subject=current_app.config['ERROR_MAIL_SUBJECT'],
            sender=current_app.config['ERROR_MAIL_SENDER'],
            recipients=current_app.config['ERROR_MAIL_RECIPIENTS'],
            body=self.get_body()
        )

    def get_traceback(self):
        '''Returns the traceback of last exception.'''
        return traceback.format_exc()

    def get_request_info(self):
        '''Returns the information about current request.'''
        rt = []
        environ = request.environ
        environkeys = sorted(environ.keys())
        for key in environkeys:
            rt.append('{}: {}'.format(key, environ.get(key)))
        return '\n'.join(rt)


mail_on_500 = ErrorMail
'''An alias for compatibility with previous versions.'''


__all__ = ['mail_on_500', 'ErrorMail']
