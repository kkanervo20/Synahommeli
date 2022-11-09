import sys
import visa

#rm = visa.ResourceManager()
#rm.list_resources()
#AGILENT_33220A = rm.open_resource('USB0::0x0957::0x0407::MY44047602::INSTR')
#print(AGILENT_33220A.query('*IDN?'))


rm = visa.ResourceManager()
resource_list = rm.list_resources()

resource = ""

for index in range(len(resource_list)):
	if "0x0957::0x0407::" in resource_list[index]:
		resource = resource_list[index]
		break

if resource != "":
	AGILENT_33220A = rm.open_resource(resource)
	print(AGILENT_33220A.query('*IDN?'))
else:
	print "Error: Agilent 33220A not connected."
	sys.exit()



AGILENT_33220A.write('*RST')
AGILENT_33220A.write('FUNCtion SINusoid')
AGILENT_33220A.write('OUTPut:LOAD 50')
AGILENT_33220A.write('VOLTage 4')
AGILENT_33220A.write('FREQuency 25000')
AGILENT_33220A.write('OUTPut ON')
AGILENT_33220A.write('FREQuency 26000')
AGILENT_33220A.write('SWEep:STATe ON') 
AGILENT_33220A.write('FREQuency:STARt 1000') 
AGILENT_33220A.write('FREQuency:STOP 10000') 
AGILENT_33220A.write('SWEep:TIME 0.3') 
AGILENT_33220A.write('MARKer:FREQuency 2000') 
AGILENT_33220A.write('MARKer On')