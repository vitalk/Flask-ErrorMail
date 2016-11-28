#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from flask import Flask
from flask import url_for


def test_send_mail_on_error(client, outbox):
    client.get(url_for('should_fail'))

    assert outbox

    mail, = outbox
    assert mail.subject == '[Flask|ErrorMail] Exception Detected'
    assert mail.sender == 'noreply@localhost'
    assert mail.recipients == ['admin@example.com']
    assert 'Hi there' in mail.body
    assert 'Traceback' in mail.body
    assert 'Request Information' in mail.body


@pytest.mark.options(error_mail_subject='Oops! I did it again')
def test_configure_mail_subject(client, outbox):
    client.get(url_for('should_fail'))
    mail, = outbox

    assert mail.subject == 'Oops! I did it again'


@pytest.mark.options(error_mail_sender='Alice')
def test_configure_mail_sender(client, outbox):
    client.get(url_for('should_fail'))
    mail, = outbox

    assert mail.sender == 'Alice'


@pytest.mark.options(error_mail_recipients=['this@example.com', 'that@example.com'])
def test_configure_mail_recipients(client, outbox):
    client.get(url_for('should_fail'))
    mail, = outbox

    assert mail.recipients == ['this@example.com', 'that@example.com']
