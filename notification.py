import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def prep_email(sender,receiver,msg,subject=""):
   email = MIMEMultipart()
   email['Subject'] = subject
   email['From'] = sender
   email['To'] = receiver
   email.attach(MIMEText(msg,'plain'))
   return email

def send_email(sender,receiver,msg,pwd):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, pwd)
    text = msg.as_string()
    try:
        server.sendmail(sender, receiver, text)
        server.quit()
        return "success"
    except Exception as e:
        server.quit()
        return e

def main():
    FROM = input("sender address: ")
    PWD = input("sender password: ")
    TO = input("receiver address: ")
    SUBJECT = input("enter subject (optional): ")
    MESSAGE = input("enter message: ")

    mail = prep_email(FROM,TO,MESSAGE,SUBJECT)
    result = send_email(FROM,TO,mail,PWD)
    print(result)

if __name__ == "__main__":
    main()
