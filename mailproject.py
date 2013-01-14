#!/usr/bin/env python
# mailproject.py --cust-type=<Customer Type> < Mail Message
# Takes the body of the mail message on STDIN.
#

from optparse import OptionParser
import ConfigParser
import psycopg2
import smtplib
import sys
from email.parser import Parser
from mako.template import Template

# Process out command line arguements.

parser = OptionParser()
parser.add_option("--cust-type",
		          action="store",
				  type="string",
				  dest="cust_type",
				  help="Which customer type do we want to mass mail?")
(options, args) = parser.parse_args()

# Open up our config file that will contain all of our configuration
# information.

config = ConfigParser.SafeConfigParser()
config.read('mailproject.cfg')

# Set up our database connection so we can query our xTuple to get a set of 
# people to send an email to.

conn = psycopg2.connect(database = config.get("Database","dbname"), 
		user = config.get("Database","user"),
		password = config.get("Database","password"),
		host = config.get("Database","host"))
cur = conn.cursor()

if config.get("Mailserver","ssl") == "true":
	print "SSL"
	mailserver = smtplib.SMTP_SSL(config.get("Mailserver","host"),config.get("Mailserver","port"))
else:
	print "Not-SSL"
	mailserver = smtplib.SMTP(config.get("Mailserver","host"),config.get("Mailserver","port"))

print "Read Standard in now!"
email = Parser().parse(sys.stdin)
print "End of standard in!"
# Main Body!

cur.execute('SELECT customer_number, customer_name, correspond_contact_email, correspond_contact_first FROM api.customer WHERE customer_type = %s', (options.cust_type, ))
custlist = cur.fetchall()

for cust in custlist:
	(cust_number, cust_name, contact_email, contact_first) = cust
	print cust
	email.replace_header('To', contact_email)
	mytemplate = Template(email.as_string())
	print mytemplate.render(cust_name=cust_name, contact_email=contact_email, contact_first=contact_first)
#	mailserver.sendmail(email['From'],email['To'], email.as_string())

# Clean everything up!
mailserver.quit()
cur.close()
conn.close()
