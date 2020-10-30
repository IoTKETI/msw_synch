from tis.oneM2M import *
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

        # OS address bit check
        (os_bit, _) = platform.architecture()
        if os_bit == '32bit':
            self.client_sw = './msw_timesync_msw_timesync/device/linux_client_x86'
        elif os_bit == '64bit':
            self.client_sw = './msw_timesync_msw_timesync/device/linux_client_x64'

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
            data_temp = offset.split('+')
            payload = dict()
            payload['server'] = data_temp[0]
            payload['mc_time'] = data_temp[1]
            payload['mc_offset'] = data_temp[2]
            payload['fc_time'] = data_temp[1]
            payload['fc_offset'] = data_temp[2]
            payload = json.dumps(payload, indent=4)
#             payload = json.loads(payload)

            # Time offset check
            if abs(float(data_temp[2])) > float(self.threshold):

                # Excute synchronizer
                subprocess.call([self.client_sw, '1', self.server_addr, self.server_port, str(self._protocol), str(self.threshold)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                print('Synchronizer is excuted')

            # Return the calculated time offset
            return payload

        else :
            pass
