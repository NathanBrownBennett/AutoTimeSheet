from app import db, SMTPConfig

def configure_smtp():
    # Prompt user for email configuration
    mail_server = input("Enter mail server: ")
    mail_port = int(input("Enter mail port: "))
    use_tls = input("Use TLS (True/False)?: ").lower() in ['true', '1', 't']
    username = input("Enter mail username: ")
    password = input("Enter mail password: ")
    default_sender = input("Enter default sender email: ")

    # Check if there's an existing configuration and update it, otherwise create a new one
    smtp_config = SMTPConfig.query.first()
    if smtp_config:
        smtp_config.mail_server = mail_server
        smtp_config.mail_port = mail_port
        smtp_config.use_tls = use_tls
        smtp_config.username = username
        smtp_config.password = password
        smtp_config.default_sender = default_sender
    else:
        new_config = SMTPConfig(mail_server=mail_server, mail_port=mail_port, use_tls=use_tls, username=username, password=password, default_sender=default_sender)
        db.session.add(new_config)
    
    db.session.commit()
    print("SMTP configuration saved successfully.")

if __name__ == "__main__":
    configure_smtp()