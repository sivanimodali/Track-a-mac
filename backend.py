#!/usr/bin/python
import easysnmp
from easysnmp import Session
from sqlite3 import Error
import sqlite3
import time
import datetime
import math 


VL = 'DEFAULT_VLAN(1)'

def probe_device(ip, port, community, version, conn):
	oids = {'dot1dTpFdbEntryAddress':'1.3.6.1.2.1.17.4.3.1.1',
			'dot1dTpFdbEntryPort':'1.3.6.1.2.1.17.4.3.1.2',
			'dot1qTpFdbEntryStatus':'1.3.6.1.2.1.17.4.3.1.3',
			'dot1qTpFdbAddress':'1.3.6.1.2.17.7.1.2.2.1.1',
			'dot1qTpFdbPort':'1.3.6.1.2.1.17.7.1.2.2.1.2',
			'dot1qTpFdbStatus':'1.3.6.1.2.1.17.7.1.2.2.1.3',
			'dot1qVlanStaticName':'1.3.6.1.2.1.17.7.1.4.3.1.1',
			'sysDescr':'1.1.3.6.1.2.1.1.1',
			'dot1dBasePortIfIndex':'1.3.6.1.2.1.17.1.4.1.2',
			'vlans':'1.3.6.1.2.1.17.7.1.4.3.1.4'}

	try:
		session = Session(hostname=ip, remote_port=port, version=version, community=community)
	except Exception as e:
		print(e)
		failed_attempts = conn.execute("SELECT FAILED_ATTEMPTS from info where IP=?, PORT=?",(ip,port))
		failed_attempts = failed_attempts + 1
		conn.execute("UPDATE info set FAILED_ATTEMPTS=? where (IP=? and PORT=?)",(failed_attempts,ip,port))
		conn.commit()
	starting_time = str(datetime.datetime.now())
	try:
		mac_address = session.walk(oids['dot1dTpFdbEntryAddress'])
		port_details = session.walk(oids['dot1dTpFdbEntryPort'])
		for i,j in zip(mac_address, port_details):
			oid = i.oid;
			oid_index_place = i.oid_index;
			snmp_type=i.snmp_type;
			mac = ':'.join('{:02x}'.format(ord(a)) for a in i.value)
			port_value = j.value
		  
			information = conn.execute("SELECT * from List where (PORT=? and IP=?)",(port_value,ip))
			gather_information = information.fetchall()
			for mac_address_connection in gather_information:
				i = mac_address_connection[3]
			if len(gather_information) == 0:
				conn.execute('''INSERT INTO List(IP, VLANs, PORT, MACS) values (?,?,?,?)''',(ip,VL,port_value,mac))
				conn.commit()
			elif len(gather_information) == 1 and i.find(mac) == -1:
				mac_result = i + "," + mac
				conn.execute("UPDATE List set MACS=? where PORT=?",(mac_result,port_value))
				conn.commit()
		number_of_vlan = []
		name_of_vlan = []
		vlans = session.walk(oids['vlans'])
		index_of_vlan = session.walk(oids['dot1qVlanStaticName'])
		storing_values = []
		oids_of_vlan = []
		for index, vlan in zip(index_of_vlan, vlans):
			value = ':'.join('{:02x}'.format(ord(x)) for x in vlan.value)
			storing_values = value.split(':')
			oid = vlan.oid
			oids_of_vlan.append(oid)
			vlan_name = index.value
			count_of_vlan = oid.split('.')
			num_of_vlan = str(count_of_vlan[-1])
			combine = ''
			if vlan_name != VL :
				starting=0
	 			while starting < (len(storing_values)):
					hexlist = storing_values
					mac_hex = hexlist[starting]
					scale = 16
					number_of_bits = 8
					orghex = bin(int(mac_hex, scale))[2:].zfill(number_of_bits)
					combine = combine + str(orghex)
					orghex = ''
					listvls = list(combine)
					starting =starting+1
				another=0
				for k in range(len(listvls)):
					if listvls[k] == '1':
						num = k + 1
						name_of_vlan.append(str(vlan_name) + '(' + num_of_vlan + ')')
						number_of_vlan.append(num)
		final_result=0
		while final_result < (len(number_of_vlan)):
			portlan = '1'
			conn.execute("UPDATE List set VLANs = ? where PORT=?", (name_of_vlan[final_result],number_of_vlan[final_result]))
			conn.commit()
			final_result+=1
	except Exception as e:
		print(str(e)+' '+str(ip)+":"+str(port))
	finish_time = str(datetime.datetime.now())

	conn.execute("UPDATE info set FIRST_PROBE=?, LATEST_PROBE=? where (IP=? and PORT=?)",(starting_time, finish_time, ip, port))
	conn.commit()


while True:
	conn = None
	conn = sqlite3.connect('mydatabase.db')

	if conn:
		information = conn.execute('Select * from info')
		for items in information:
			ip = items[0]; port=int(items[1]); community=items[2]; version=int(items[3])
			probe_device(ip, port, community,version, conn)

		conn.close()

	time.sleep(60)