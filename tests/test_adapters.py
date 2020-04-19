import logging
import os

import pytest
import requests

from jumpssh import restclient, SSHSession
from . import util as tests_util


REMOTE_HOST_IP_PORT = 'remotehost:5000'


@pytest.fixture(scope="module")
def docker_env():
    docker_compose_env = tests_util.DockerEnv(os.path.join("docker", "docker-compose_restclient.yaml"))
    yield docker_compose_env
    docker_compose_env.clean()


def test_requests(docker_env):
    gateway_ip, gateway_port = docker_env.get_host_ip_port('gateway')

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

        http_response = http_session.post('http://%s/echo-method' % REMOTE_HOST_IP_PORT, json={'key': 'value'})
        assert http_response.status_code == 200

        assert 'request-method' in http_response.headers

        #assert http_response.headers == {}
        #assert http_response.content == u'Hello, World!'
