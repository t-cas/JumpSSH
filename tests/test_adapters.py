import logging

import pytest
import requests

from jumpssh import restclient, SSHSession
from . import util as tests_util

logging.basicConfig()


@pytest.fixture(scope="function")
def docker_env():
    my_docker_env = tests_util.DockerEnv()
    my_docker_env.start_host('image_sshd', 'gateway')
    my_docker_env.start_host('image_restserver', 'remotehost')
    yield my_docker_env  # provide the fixture value
    print("teardown docker_env")
    my_docker_env.clean()


def test_requests(docker_env):
    gateway_ip, gateway_port = docker_env.get_host_ip_port('gateway')
    remotehost_ip, remotehost_port = docker_env.get_host_ip_port('remotehost', private_port=5000)

    with SSHSession(host=gateway_ip, port=gateway_port, username='user1', password='password1') as gateway_session:
        channel = gateway_session.ssh_transport.open_session()
        #print(channel.getpeername())

        # raise error rather than blocking the call
        channel.setblocking(True)

        #assert not channel.closed

        adapter = restclient.HttpSshAdapter(channel=gateway_session.ssh_transport.sock, timeout=5)
        http_session = requests.session()
        http_session.mount("http://", adapter)
        # s.mount("https://", adapter)

        http_response = http_session.post('http://%s:%s/echo-method' % (tests_util.get_host_ip(), remotehost_port),
                                          json={'key': 'value'})
        assert http_response.status_code == 200

        assert 'request-method' in http_response.headers

        #assert http_response.headers == {}
        #assert http_response.content == u'Hello, World!'
