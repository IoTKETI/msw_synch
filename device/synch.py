from tis.oneM2M import *
from datetime import datetime as dt
from pytz import timezone
import os
import subprocess
import platform
import json
# Warning!! In each class, one must implement only one method among get and control methods


# Uplink class (for time offset monitoring)
class Monitor(Thing):

    # Initialize
    def __init__(self):
        Thing.__init__(self)
        self.protocol = 'up'
        self.interval = 5
        self.topic = []
        self.name = 'Monitor'
        self.server_addr = ''
        self.server_port = ''
        self.trans_protocol = 'udp'
        self.threshold = 5
        self.synch_process = []
        self.ct_path = ''

        # client path check
        if os.path.exists('./linux_client_x86'):
            self.ct_path = os.path.abspath('linux_client_x86')
        elif os.path.exists('./device/linux_client_x86'):
            self.ct_path = os.path.abspath('./device/linux_client_x86')
        else:
            for name in os.listdir('./'):
                if name.find('_timesync') != -1:
                    if os.path.exists('./' + name + '/linux_client_x86'):
                        self.ct_path = os.path.abspath('./' + name + '/linux_client_x86')
                        break
                    elif os.path.exists('./' + name + '/device/linux_client_x86'):
                        self.ct_path = os.path.abspath('./' + name + '/device/linux_client_x86')
                        break
        
        print(self.ct_path)

        # OS address bit check
        (os_bit, _) = platform.architecture()
        if os_bit == '32bit':
            self.client_sw = self.ct_path[:-2] + '86'
        elif os_bit == '64bit':
            self.client_sw = self.ct_path[:-2] + '64'

        # Change of ownership
        subprocess.call(['sudo', 'chmod', '777', self.client_sw])

        if self.trans_protocol == 'tcp':
            self._protocol = 1
        elif self.trans_protocol == 'udp':
            self._protocol = 0


    # Thing dependent get function
    def get(self, key):

        if key in self.topic:
            
            # Time offset calculation
            offset = subprocess.getoutput( self.client_sw + ' 3 ' + self.server_addr + ' ' + self.server_port + ' ' + str(self._protocol) )
            print(offset)
            
            data_temp = offset.split('+')
            del data_temp[-1]
            print(data_temp)
            
            payload = dict()
            payload['server'] = dt.fromtimestamp( float( data_temp[0] ), ).astimezone(timezone('Asia/Seoul')).strftime('%Y%m%dT%H%M%S%f')[:-3]
            payload['mc_time'] = dt.fromtimestamp( float( data_temp[1] ), ).astimezone(timezone('Asia/Seoul')).strftime('%Y%m%dT%H%M%S%f')[:-3]
            payload['mc_offset'] = int( data_temp[2] )
            payload['fc_time'] = dt.fromtimestamp( float( data_temp[1] ), ).astimezone(timezone('Asia/Seoul')).strftime('%Y%m%dT%H%M%S%f')[:-3]
            payload['fc_offset'] = int( data_temp[2] )
            payload = json.dumps(payload, indent=4)

            # Time offset check
            if abs(float(data_temp[2])) > float(self.threshold):
                # Excute synchronizer
                subprocess.call([self.client_sw, '1', self.server_addr, self.server_port, str(self._protocol), str(self.threshold)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                print('Synchronizer is excuted')

            # Return the calculated time offset
            return payload

        else :
            pass
