import os
from os import getcwd
from os.path import join
import time
import pytest

from atomic_p2p.peer import Peer
from atomic_p2p.peer.dns_resolver import DNSResolver
from atomic_p2p.utils.security import self_hash as sh, create_self_signed_cert


@pytest.fixture(scope='session')
def dns_resolver():
    return DNSResolver(ns='127.0.0.1', role='switch')


@pytest.fixture(scope='session')
def self_hash():
    return sh(join(os.getcwd(), 'atomic_p2p'))


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
