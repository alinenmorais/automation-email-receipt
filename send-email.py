#!/usr/bin/python3

import smtplib, ssl, csv, sys, os
from time import sleep
from getpass import getpass
from datetime import datetime

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Server Email data
sender_name = input("Seu nome: ")
sender_email = input("Seu email: ")
sender_pass = getpass("Email password: ")
smtp_server = "smtp.gmail.com"
port = 587  # starttls

# Email content
months = {1: "Janeiro", 2: "Feveiro", 3: "Março", 4: "Abril", 5: "Junho", 6: "junho",
          7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
subject = f"Contracheque de {months[datetime.now().month]}"
body = f"Segue anexo o seu contracheque.\n\nAtt, {sender_name}"


def anpayck(names):
    """"Analizes if all paychecks exist"""

    files = os.listdir("files/")

    # Format files
    for n in range(len(files)):
        file = files[n].split(".")[0].split("-")  # remove ".pdf" and "-"
        files[n] = " ".join(file)

    # Anylizes all files
    not_found, counter = [], 0
    for name in names:
        counter += 1
        print(f"[+] Analisando contracheques ... {counter}", end="\r")
        if name not in files:
            not_found.append(name)
        sleep(0.25)
    print(f"[+] Analisando contracheques ... {counter} OK")

    # Not found feedback
    if not_found:
        print(f"[-] Contracheques não encontrados ...")
        sleep(1)
        for name in not_found:
            print(f"    {name}")
            sleep(0.25)
        sleep(1)
        print(f"[-] Confira os arquivos e tente novamente.")
        sys.exit()


def mtaconn(sender_email, passwd):
    """Try to connect to MTA"""

    context = ssl.create_default_context()  # create a secure SSL context
    try:
        print("[+] Conectando-se ao servidor e Email ...", end=" ", flush=True)
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # ban be omitted
        server.starttls(context=context)  # secure the connection
        server.ehlo()  # can be omitted
        server.login(sender_email, passwd)

        print("OK")

        return server
    except Exception:
        print("FAIL")
        print("[-] Conexão falhou! Tente novamente.")
        sys.exit()


def mkmsg(receiver_email, initial_body, paycheck_file):
    """Create a multipart message and set headers"""

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # recommended for mass emails

    # Add body to email
    full_body = initial_body + body
    message.attach(MIMEText(full_body, "plain"))

    # Adding Attachments
    attach_file = paycheck_file

    with open(attach_file, "rb") as attachment:  # open file in binary mode
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)  # encode file in ASCII characters to send by email

    part.add_header(  # add header as key/value pair to attachment part
        "Content-Disposition",
        f"attachment; filename= {attach_file}",
    )

    # add attachment to message and convert message to string
    message.attach(part)

    return message.as_string()


def sendmail(name, receiver_email, message):
    """Try to send email"""

    try:
        print(f"    {name} ...", end=" ", flush=True)
        mta_conn.sendmail(sender_email, receiver_email, message)
        print("OK")
        sleep(0.25)

    except Exception:
        print()


if __name__ == "__main__":
    # Analyzes paychecks
    with open("staff.csv") as file:
        reader = csv.reader(file)
        next(reader)  # skip first line (header)

        names = []
        for name in reader:  # create a list with just the names
            names.append(name[0].lower())
        anpayck(names)

    # Send Emails
    with open("staff.csv") as file:
        reader = csv.reader(file)
        next(reader)  # skip first line (header)

        mta_conn = mtaconn(sender_email, sender_pass)  # try connect to mta

        print("[+] Enviando emails ... ")
        sleep(2)
        counter = 0
        for name, email in reader:
            paycheck_file = f"files/{name.lower().replace(' ', '-')}.jpg"  # path to pdf

            initial_body = f"Olá, {name.split()[0]}!\n\n"  # "Olá, Fulano!""
            message = mkmsg(email, initial_body, paycheck_file)

            sendmail(name, email, message)
            counter += 1

    mta_conn.quit()
    print(f"[+] Emails enviados: {counter}")
