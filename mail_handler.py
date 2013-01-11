import smtplib
from email.mime.text import MIMEText

class cernMail():
    """Prepare and send emails to any address with bcc option"""
    
    # set mail servers params
    _server = "cernmx.cern.ch"
    _port = 25
    _from = None
    _to = None
    _bcc = []
    _subject = None
    _body = None

    def __init__(self, fro, to, subject, body):
        self._from = fro
        self._to = to
        self._subject = subject
        self._body = MIMEText(body)

    def send(self):
        """Send email"""
        s = smtplib.SMTP(self._server, self._port)

        self._body['Subject'] = self._subject
        self._body['From'] = self._from
        self._body['To'] = ", ".join(self._to)

        s.sendmail(self._from, self._to + self._bcc, self._body.as_string())
            
        s.quit()
