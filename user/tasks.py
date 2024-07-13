from django import conf, template, core
from celery import shared_task


@shared_task(name="email_welcome_message")
def email_welcome_message(username, email_address):
    _html = "user/emails/welcome.html"
    _context = {
        "username": username,
        "site": conf.settings.SITE_NAME,
        "url": conf.settings.USER_URL,
    }
    _content = template.loader.render_to_string(_html, _context)
    _email = core.mail.EmailMessage(
        f"Welcome to {conf.settings.SITE_NAME}",
        _content,
        conf.settings.EMAIL_SENDER,
        [email_address],
    )
    _email.send()


@shared_task(name="email_forget_password")
def email_forget_password(uid, token, email_address):
    _html = "user/emails/forget_password.html"
    _context = {
        "uid": uid,
        "token": token,
        "site": conf.settings.SITE_NAME,
        "url": conf.settings.USER_URL,
    }
    _content = template.loader.render_to_string(_html, _context)
    _email = core.mail.EmailMessage(
        f"{conf.settings.SITE_NAME} - Password recovery instructions",
        _content,
        conf.settings.EMAIL_SENDER,
        [email_address],
    )
    _email.send()
