import os
from os import getcwd
from os.path import join
import time
import pytest

from LibreCisco.peer import Peer
from LibreCisco.peer.pool_maintainer import PoolMaintainer
from LibreCisco.device import DeviceManager
from LibreCisco.utils.security import self_hash as sh, create_self_signed_cert


@pytest.fixture(scope='session')
def pool_maintainer():
    return PoolMaintainer(ns='127.0.0.1', role='switch', domain='yunnms.lalala.org')


@pytest.fixture(scope='session')
def self_hash():
    return sh(join(os.getcwd(), 'LibreCisco'))


@pytest.fixture(scope='session')
def cert():
    return create_self_signed_cert(getcwd(), 'data/test.pem', 'data/test.key')


@pytest.yield_fixture(scope='module')
def default_peer(cert, self_hash):
    p = Peer(host=('0.0.0.0', 8000), name='name', role='role', cert=cert,
             _hash=self_hash)
    p.start()

    yield p
    time.sleep(1)
    p.stop()


@pytest.yield_fixture(scope='module')
def default_peer2(cert, self_hash):
    p = Peer(host=('0.0.0.0', 8001), name='name2', role='role', cert=cert,
             _hash=self_hash)
    p.start()
    yield p
    time.sleep(1)
    p.stop()


@pytest.yield_fixture(scope='module')
def default_device_manager(default_peer):
    d = DeviceManager(peer=default_peer)
    d.start()

    yield d
    time.sleep(1)
    d.stop()
