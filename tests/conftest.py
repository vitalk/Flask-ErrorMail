#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from flask import Flask
from flask import Blueprint
from flask import abort
from flask_mail import Mail
from flask_errormail import ErrorMail
from flask_errormail import mail_on_500


@pytest.fixture
def app():
    app = Flask(__name__)
    app.debug = True
    app.testing = True

    @app.route('/should-fail')
    def should_fail():
        abort(500, 'Hi there')

    return app


@pytest.fixture
def app_with_blueprint(app):
    bp = Blueprint('bp', __name__)

    @bp.route('/bp-should-fail')
    def should_fail():
        abort(500, 'An error in blueprint')

    app.register_blueprint(bp)
    return app


@pytest.fixture(autouse=True)
def mail(request):
    if 'app' not in request.fixturenames:
        return

    app = request.getfuncargvalue('app')
    return Mail(app)


@pytest.fixture(autouse=True, params=[ErrorMail, mail_on_500])
def error_mail(request):
    if 'app' not in request.fixturenames:
        return

    app = request.getfuncargvalue('app')
    return request.param(app)


@pytest.yield_fixture
def outbox(mail):
    with mail.record_messages() as outbox:
        yield outbox
