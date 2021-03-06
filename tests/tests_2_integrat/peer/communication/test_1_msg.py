import time
from atomic_p2p.peer.communication.net import JoinHandler


def test_send(core1, switch1):
    switch1.onProcess(['join', '127.0.0.1:{}'.format(core1.server_info.host[1])])
    time.sleep(5)
    switch1.onProcess(['send', '127.0.0.1:{}'.format(core1.server_info.host[1]),
                       '123'])
    time.sleep(8)
    assert '123' in core1.last_output


def test_broadcast(core1, switch1, switch2):
    switch1.onProcess(['join', '127.0.0.1:{}'.format(core1.server_info.host[1])])
    switch2.onProcess(['join', '127.0.0.1:{}'.format(core1.server_info.host[1])])
    time.sleep(5)

    core1.onProcess(['send', 'broadcast:sw', 'ttt'])
    time.sleep(8)
    assert 'ttt' in switch1.last_output, switch1.last_output
    assert 'ttt' in switch2.last_output, switch2.last_output
