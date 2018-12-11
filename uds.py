
import udsoncan
from udsoncan.connections import BaseConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *


import sys
J2534.SetErrorLog(True)

try:
    index = int(sys.argv[1], base=10)
except:
    index = 0
J2534.setDevice(index)

class J2534Connect(BaseConnection):
    def open(self):
        pass
    def close(self):
        pass
    def 
    pass

conn = J2534Connect('can0')
with Client(conn,  request_timeout=2) as client:
   try:
      client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)  # integer with value of 3
      client.unlock_security_access(MyCar.debug_level)   # Fictive security level. Integer coming from fictive lib, let's say its value is 5
      vin = client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, 'ABC123456789')       # Standard ID for VIN is 0xF190. Codec is set in the client configuration
      print('Vehicle Identification Number successfully changed.')
      client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
   except NegativeResponseException as e:
      print('Server refused our request for service %s with code "%s" (0x%02x)' % (e.response.service.get_name(), e.response.code_name, e.response.code))
   except InvalidResponseException, UnexpectedResponseException as e:
      print('Server sent an invalid payload : %s' % e.response.original_payload)