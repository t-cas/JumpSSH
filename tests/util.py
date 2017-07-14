from __future__ import print_function
import datetime
import json
import os
import random
import socket
import string

import docker
import docker.errors
import requests.exceptions


class DockerEnv(object):
    def __init__(self):
        self.cli = DockerEnv.get_cli()
        self.hosts = {}

    @staticmethod
    def get_cli():
        if os.environ.get('DOCKER_HOST'):
            docker_cli = docker.from_env()
        else:
            docker_cli = docker.Client(base_url='unix://var/run/docker.sock')
        # check access to docker
        try:
            docker_cli.info()
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to access Docker daemon. Are you sure Docker is started ?")
        return docker_cli

    def get_host_ip_port(self, name, private_port=22):
        docker_host = self.hosts.get(name)
        if docker_host:
            return docker_host.get_host_ip_port(private_port=private_port)

    def start_host(self, image_type, hostname, linux_distribution):
        if hostname in self.hosts:
            raise Exception("host with name '%s' already exists")
        try:
            self.hosts[hostname] = DockerHost(self.cli, image_type, hostname, linux_distribution)
        except docker.errors.DockerException:
            self.clean()
            raise

    def clean(self):
        for docker_host in self.hosts.values():
            docker_host.clean()


class DockerHost(object):
    def __init__(self, cli, image_type, hostname, linux_distribution):
        self.cli = cli
        self.hostname = hostname
        self.image_type = image_type
        self.linux_distribution = linux_distribution

        self.image_name = '%s_%s' % (self.image_type, self.linux_distribution)
        self.container_id = None

        # no image with that name currently exists, build it
        if len(self.cli.images(name='jumpssh/%s' % self.image_name)) == 0:
            self.build_image()

        container = self.cli.create_container(
            image='jumpssh/%s:latest' % self.image_name,
            detach=True,
            name='jumpssh_%s_%s' % (hostname, datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
            hostname='%s.example.com' % hostname,
            host_config=self.cli.create_host_config(publish_all_ports=True))

        self.container_id = container['Id']
        self.cli.start(container=self.container_id)

    def get_host_ip_port(self, private_port):
        container_host_info_list = self.cli.port(container=self.container_id, private_port=private_port)
        if len(container_host_info_list) > 0:
            host_ip = container_host_info_list[0]['HostIp']
            host_port = int(container_host_info_list[0]['HostPort'])
            return host_ip, host_port

    def build_image(self):
        dockerfile_path = os.path.join(os.path.dirname(__file__), 'docker', self.image_type, self.linux_distribution)
        if not os.path.isfile(os.path.join(dockerfile_path, 'Dockerfile')):
            raise Exception("Missing Dockerfile in '%s'" % dockerfile_path)
        for line in self.cli.build(
                path=dockerfile_path,
                rm=True,
                forcerm=True,
                tag='jumpssh/%s' % self.image_name):
            try:
                json_line = json.loads(line.decode('utf-8').strip())
                if 'stream' in json_line:
                    print(json_line['stream'].rstrip())
            except ValueError:
                pass
                # interesting build output is only the valid json one

    def clean(self):
        self.cli.stop(container=self.container_id)
        self.cli.remove_container(container=self.container_id)
        # by default delete generated docker images
        if int(os.environ.get('JUMPSSH_DOCKER_IMAGES_CLEANUP', '1')) != 0:
            try:
                self.cli.remove_image(image='jumpssh/%s' % self.image_name)
            except docker.errors.APIError as ex:
                # image can be used by several containers, in that case, it should be removed after removal
                # of the last container using that image
                if ex.response.status_code != 409:
                    raise


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    return local_ip_address


def create_random_json(size=1000):
    random.seed()
    dummy_json = {}
    for i in range(size):
        random_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        random_value = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(100))
        dummy_json[random_key] = random_value
    return dummy_json
