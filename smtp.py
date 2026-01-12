import smtplib
from getpass import getpass

sender_email = 'faaizhaikal@gmail.com'.strip()
sender_password = 'jcqs hlyn mdtr pksh'
# sender_password = getpass('Enter your password: ')

recipient_email = 'faaizhilmi77@gmail.com faaizhaikal@gmail.com'.strip().split()

print(recipient_email)

subject = input('Enter subject: ')

body_lines = ("From: %s\r\nTo: %s\r\n\r\n"
              % (sender_email, ", ".join(recipient_email)))

print('Enter message:')
while True:
  try:
    line = input()
  except EOFError:
    break
  
  if not line:
    break
  
  body_lines = body_lines + line
  
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(sender_email, sender_password)
server.sendmail(sender_email, recipient_email, body_lines)
server.quit()