import time

from LibreCisco.peer.entity.peer_status import StatusType
from LibreCisco.utils import printText
from LibreCisco.utils.communication import Packet, Handler


class CheckHandler(Handler):

    def __init__(self, monitor):
        super(CheckHandler, self).__init__(pkt_type='monitor_check',
                                           peer=monitor.peer)
        self.monitor = monitor
        self.output_field = self.peer.output_field

    def on_send_pkt(self, target):
        data = {'send_ts': time.time()}
        return Packet(dst=target, src=self.peer.peer_info.host,
                      _hash=self.peer._hash, _type=self.pkt_type, _data=data)

    def on_recv_pkt(self, src, pkt, conn):
        data = pkt.data
        message = 'WatchDog check from {}: send ts {}'.format(pkt.src,
                                                              data['send_ts'])
        if self.monitor.verbose:
            printText(message)

    def on_recv_reject_pkt(self, src, pkt, conn):
        if self.monitor.verbose:
            super(CheckHandler, self).on_recv_reject_pkt(src, pkt)
        status, peer_info = self.monitor.getStatusByHost(pkt.src)
        if status:
            status.update(status_type=StatusType.PENDING)
