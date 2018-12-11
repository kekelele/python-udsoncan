
import udsoncan
from udsoncan.connections import BaseConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *
from abc import abstractmethod
BRODCAST_ID = 0x7df
SEND_ID = 0x7e0
RECV_ID = 0x7e8

import J2534
from J2534.Define import *
import sys
J2534.SetErrorLog(True)

try:
    index = int(sys.argv[1], base=10)
except:
    index = 0
J2534.setDevice(index)



class J2534Connect(BaseConnection):
    def __init__(self, name=None):
        self.dev_status = False
        return super().__init__(name=name)
        
    def open(self):
        ret, self.deviceID = J2534.ptOpen()
        ret, self.channel = J2534.ptConnect(self.deviceID, ProtocolID.ISO15765, 0, BaudRate.B500K)
        if ret == 0:
            self.dev_status = True
        maskMsg = J2534.ptMskMsg(16)
        maskMsg.setID(0xffffffff)

        patternMsg = J2534.ptPatternMsg(16)
        patternMsg.setID(SEND_ID)

        flowcontrolMsg = J2534.ptPatternMsg(16)
        flowcontrolMsg.setID(RECV_ID)

        ret, fiterid = J2534.ptStartMsgFilter(self.channel, FilterType.FLOW_CONTROL_FILTER,
                                            maskMsg, patternMsg, flowcontrolMsg)
    def is_open(self):
    		return self.dev_status
    def close(self):
        ret = J2534.ptDisconnect(self.channel)
        ret = J2534.ptClose(self.deviceID)
    
    def specific_send(self, payload):
        data = [i for i in bytes(payload)]
        data = [len(data)] + data
        msg = J2534.ptTxMsg(ProtocolID.ISO15765, 32)
        msg.setIDandData(SEND_ID, data )
        ret = J2534.ptWtiteMsgs(self.channel, msg, 1, 100)
        if ret == 0:
            msg.show()
    def specific_wait_frame(self, timeout=2):
        msg = J2534.ptRxMsg()
        maskMsg = J2534.ptMskMsg(0)
        maskMsg.setID(0xffffffff)
        patternMsg = J2534.ptPatternMsg(0)
        patternMsg.setID(RECV_ID)

        flowcontrolMsg = J2534.ptPatternMsg(0)
        flowcontrolMsg.setID(SEND_ID)

        ret, fiterid = J2534.ptStartMsgFilter(self.channel, FilterType.FLOW_CONTROL_FILTER,
                                            maskMsg, patternMsg, flowcontrolMsg)

        ret = J2534.ptReadMsgs(self.channel, msg, 1, 100)
        if ret == 0:
            size = msg.Data[0]
            return bytes(msg.Data[1:size])
        return None
    def empty_rxqueue(self):
        pass
conn = J2534Connect('can0')
with Client(conn,  request_timeout=2) as client:
    try:
        client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)  # integer with value of 3
        #client.unlock_security_access(MyCar.debug_level)   # Fictive security level. Integer coming from fictive lib, let's say its value is 5
        vin = client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, 'ABC123456789')       # Standard ID for VIN is 0xF190. Codec is set in the client configuration
        print('Vehicle Identification Number successfully changed.')
        client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
    except NegativeResponseException as e:
        print('Server refused our request for service %s with code "%s" (0x%02x)' % (e.response.service.get_name(), e.response.code_name, e.response.code))
    except InvalidResponseException as e:
        print('Server sent an invalid payload : %s' % e.response.original_payload)