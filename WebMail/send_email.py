import smtplib
from email.mime.text import MIMEText
from email.header import Header

myemail = 'example@gmail.com'
client = 'sb.ua@ieee.org'

message = "To: "+Header("IEEE", "utf-8").encode()+" <"+client+\
    ">\nSubject: "+Header("Spam", "utf-8").encode()+"\nThis is an automated message.\n"

try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(myemail, client, message)
    print("Successfully sent email")
except:
    print("Error: unable to send email")
