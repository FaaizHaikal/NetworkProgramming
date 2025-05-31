from ftplib import FTP

f = FTP('localhost') 
f.login('faaiz', 'faaiz1203')

fd = open('test01.txt', 'wb')
f.retrbinary('RETR test01.txt', fd.write)
fd.close() 
f.quit()
