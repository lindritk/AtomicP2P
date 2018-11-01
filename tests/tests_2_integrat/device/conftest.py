import pytest
from LibreCisco.device.connection import SSHConnection, TelnetConnection


@pytest.fixture(scope='session')
def ssh(request):
    config = request.config
    host = config.getoption('--ssh-test-host').split(':')
    account = config.getoption('--ssh-account')
    passwd = config.getoption('--ssh-passwd')
    return SSHConnection(host=host, username=account, password=passwd)


@pytest.fixture(scope='session')
def telnet(request):
    config = request.config
    host = config.getoption('--telnet-test-host')
    account = config.getoption('--telnet-account')
    passwd = config.getoption('--telnet-passwd')
    return TelnetConnection(host=host, username=account, password=passwd)
