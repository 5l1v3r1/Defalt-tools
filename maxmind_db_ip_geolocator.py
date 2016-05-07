#! /usr/bin/python

#Hello fellow hackers! My name is Defalt
#I built a very basic version of this tool a long time ago (http://pastebin.com/J5NLnThL)
#Since then, my scripting skills have gotten much better, so I decided to rewrite it
#This will query the MaxMind database to get an approximate geolocation of an IP address
#If the needed module or database is not installed, it will install it for you!
#Happy hacking! -Defalt


class Locator(object):
	def __init__(self):
		self.desc = 'IP Geolocation Tool'
		self.needed_installs = False
	def import_needed(self):
		global socket; import socket
		global urllib; import urllib
		global os; import os
		global gzip; import gzip
		try:
			import pygeoip
		except ImportError:
			print '[!] Failed to Import pygeoip'
			try:
				choice = raw_input('[*] Attempt to Auto-install pygeoip? [y/N] ')
			except KeyboardInterrupt:
				print '[*] User Attempted Interrupt'
				sys.exit(1)
			if choice[0].strip().lower() == 'y':
				print '[*] Attempting to Auto-install pygeoip... ',
				sys.stdout.flush()
				import pip
				try:
					out = pip.main(['install', '-q',  'pygeoip'])
				except Exception:
					print '[FAIL]'
					sys.exit(1)
				try:
					global pygeoip; import pygeoip
				except ImportError:
					print '[FAIL]'
					sys.exit(1)
				print '[DONE]'
				self.needed_installs = True
			elif choice[0].strip().lower() == 'n':
				print '[*] User Denied Auto-install'
				sys.exit(1)
			else:
				print '[*] Invalid Decision'
				sys.exit(1)
	def parsing_func(self):
		import argparse
		global sys; import sys
		parser = argparse.ArgumentParser(description=self.desc)
		parser.add_argument('--url', help='Locate an IP based on a URL', action='store', default=False, dest='url')
		parser.add_argument('-t', '--target', help='Locate the specified IP', action='store', default=False, dest='ip')
		parser.add_argument('--dat', help='Custom database filepath', action='store', default=False, dest='datfile')
		self.args = parser.parse_args()
		if len(sys.argv) == 1:
			parser.print_help()
			sys.exit(1)
		elif (not self.args.ip) and (not self.args.url):
			print '[!] No Target Specified'
			sys.exit(1)
		elif (isinstance(self.args.ip, basestring)) and (isinstance(self.args.url, basestring)):
			print '[!] More then One Target Specified'
			sys.exit(1)
		self.import_needed()
	def check_dat(self):
		self.parsing_func()
		try:
			if os.path.isfile(self.args.datfile):
				return self.args.datfile
			else:
				print '[!] Failed to Detect Specified Dat File'
				sys.exit(1)
		except Exception:
			if os.path.isfile('/usr/share/GeoIP/GeoLiteCity.dat'):
				return '/usr/share/GeoIP/GeoLiteCity.dat'
			else:
				print '[!] Database Detection Failed'
				try:
					choice = raw_input('[*] Attempt to Auto-install Database? [y/N] ').strip().lower()[0]
				except KeyboardInterrupt:
					print '[!] User Attempted Interrupt'
					sys.exit(1)
				if choice == 'y':
					print '[*] Attempting to Auto-install Database... ',
					sys.stdout.flush()
					if os.path.isdir('/usr/share/GeoIP'):
						pass
					else:
						os.makedirs('/usr/share/GeoIP')
					try:
						get_dat = urllib.urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz', '/usr/share/GeoIP/GeoLiteCity.dat.gz')
					except Exception:
						print '[FAIL]'
						print '[!] Failed to Retrieve Database'
						sys.exit(1)
					with gzip.open('/usr/share/GeoIP/GeoLiteCity.dat.gz', 'rb') as compressed_dat:
						with open('/usr/share/GeoIP/GeoLiteCity.dat', 'wb') as new_dat:
							new_dat.write(compressed_dat.read())
					os.remove('/usr/share/GeoIP/GeoLiteCity.dat.gz')
					print '[DONE]'
					self.needed_installs = True
					return '/usr/share/GeoIP/GeoLiteCity.dat'
				elif choice == 'n':
					print '[*] User Denied Auto-install'
					sys.exit(1)
				else:
					print '[*] Invalid Decision'
					sys.exit(1)
	def query(self):
		self.database = self.check_dat()
		if isinstance(self.args.ip, basestring):
			query_obj = pygeoip.GeoIP(self.database)
			if self.needed_installs:
				print '\n[*] Querying for Records of %s...\n' %(self.args.ip)
			else:
				print '[*] Querying for Records of %s...\n' %(self.args.ip)
			try:
				record = query_obj.record_by_addr(self.args.ip)
			except Exception:
				print '[!] Failed to Find Record for %s' %(self.args.ip)
				sys.exit(1)
			for key, val in record.items():
				print '%s: %s' %(key, val)
			print '\n[*] Query Complete!'
			sys.exit(1)
		elif isinstance(self.args.url, basestring):
			query_obj = pygeoip.GeoIP(self.database)
			try:
				if self.needed_installs:
					print '\n[*] Translating %s: %s' %(self.args.url, socket.gethostbyname(self.args.url))
				else:
					print '[*] Translating %s: %s' %(self.args.url, socket.gethostbyname(self.args.url))
				url_to_ip = socket.gethostbyname(self.args.url)
			except Exception:
				print '[!] Failed to Resolve URL'
				sys.exit(1)
			print '[*] Querying for Records of %s...\n' %(url_to_ip)
			record = query_obj.record_by_addr(url_to_ip)
			for key, val in record.items():
				print '%s: %s' %(key, val)
			print '\n[*] Query Complete!'
			sys.exit(1)

try:
	locate_ip = Locator()
	locate_ip.query()
except Exception: #Emergency exit
	print '\n[!] An Unknown Error Occured'
	sys.exit(1)
except KeyboardInterrupt: #Clean up any remaining keyboard interrupts
	print '\n[!] User Interrupted Process'
	sys.exit(1)
