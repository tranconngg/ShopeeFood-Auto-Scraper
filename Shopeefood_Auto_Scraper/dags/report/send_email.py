import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send_email(**kwargs):
        report_df = kwargs['ti'].xcom_pull(task_ids='process_report')
        send_email="trancongit11@gmail.com"
        receiver_email="trancongit11@gmail.com"

        subject = "Báo cáo thống kê cửa hàng (spf) khu vực Hà Nội"

        html_table = report_df.to_html(index=False)
        html_content = f"""
        <html>
        <head>
            <style>
                table, th, td {{
                    border: 1px solid black;
                    border-collapse: collapse;
                    padding: 8px;
                }}
                th {{
                    background-color: #f2f2f2;
                    text-align: center;
                }}
                td {{
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h2>{subject}</h2>
            <p>Đây là báo cáo thống kê các cửa hàng theo khu vực:</p>
            {html_table}
        </body>
        </html>
        """
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = send_email
        msg['To'] = receiver_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
 
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(send_email, "kghxetbrqlpzxzoy") 
        server.sendmail(send_email, receiver_email, msg.as_string())
        server.quit()

        print("Email vừa được gửi thành công!")

    # send_email(report_df)
