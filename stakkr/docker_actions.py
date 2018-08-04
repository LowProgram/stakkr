# coding: utf-8
"""Docker functions to get info about containers."""

from docker.errors import NotFound, NullResource
__st__ = {'cts_info': dict(), 'running_cts': 0}


def add_container_to_network(container: str, network: str):
    """Attach a container to a network."""
    if _container_in_network(container, network) is True:
        return False

    docker_network = get_client().networks.get(network)
    docker_network.connect(container)

    return True


def block_ct_ports(service: str, ports: list, project_name: str) -> tuple:
    """Run iptables commands to block a list of port on a specific container."""
    try:
        container = get_client().containers.get(get_ct_item(service, 'id'))
    except (LookupError, NullResource):
        return (False, '{} is not started, no port to block'.format(service))

    status, iptables = container.exec_run(['which', 'iptables'])
    iptables = iptables.decode().strip()
    if iptables == '':
        return (True, "Can't block ports on {}, is iptables installed ?".format(service))

    _allow_contact_subnet(project_name, container)

    # Now for each port, add an iptable rule
    for port in ports:
        rule = ['OUTPUT', '-p', 'tcp', '--dport', port, '-j', 'REJECT']
        try:
            container.exec_run([iptables, '-D'] + rule)
        finally:
            container.exec_run([iptables, '-A'] + rule)

    return (False, 'Blocked ports {} on container {}'.format(', '.join(ports), service))


def check_cts_are_running(project_name: str):
    """Throw an error if cts are not running."""
    get_running_containers(project_name)
    if __st__['running_cts'] is 0:
        raise SystemError('Have you started your server with the start action ?')


def container_running(container: str):
    """Return True if the container is running else False."""
    try:
        return get_api_client().inspect_container(container)['State']['Running']
    except (NotFound, NullResource):
        return False


def create_network(network: str):
    """Create a Network."""
    if network_exists(network):
        return False

    return get_client().networks.create(network, driver='bridge').id


def get_api_client():
    """Return the API client or initialize it."""
    if 'api_client' not in __st__:
        from docker import APIClient, utils
        params = utils.kwargs_from_env()
        base_url = None if 'base_url' not in params else params['base_url']
        tls = None if 'tls' not in params else params['tls']

        __st__['api_client'] = APIClient(base_url=base_url, tls=tls)

    return __st__['api_client']


def get_client():
    """Return the client or initialize it."""
    if 'client' not in __st__:
        from docker import client
        __st__['client'] = client.from_env()

    return __st__['client']


def get_ct_item(compose_name: str, item_name: str):
    """Get a value from a container, such as name or IP."""
    if 'cts_info' not in __st__:
        raise LookupError('Before getting an info from a ct, run check_cts_are_running()')

    for ct_id, ct_data in __st__['cts_info'].items():
        if ct_data['compose_name'] == compose_name:
            return ct_data[item_name]

    return ''


def get_ct_name(container: str):
    """Return the system name of a container, generated by docker-compose."""
    ct_name = get_ct_item(container, 'name')
    if ct_name == '':
        raise LookupError('{} does not seem to be started ...'.format(container))

    return ct_name


def get_network_name(project_name: str):
    """Find the full network name."""
    try:
        guessed_network_name = project_name.replace('-', '') + '_stakkr'
        network = get_client().networks.get(guessed_network_name)
    except NotFound:
        raise RuntimeError("Couldn't identify network (check your project name)")

    return network.name


def get_subnet(project_name: str):
    """Find the subnet of the current project."""
    network_name = get_network_name(project_name)
    network_info = get_client().networks.get(network_name).attrs

    return network_info['IPAM']['Config'][0]['Subnet'].split('/')[0]


def get_switch_ip():
    """Find the main docker daemon IP to add routes."""
    import socket

    cmd = r"""/bin/sh -c "ip addr show hvint0 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'" """
    res = get_client().containers.run(
        'alpine', remove=True, tty=True, privileged=True,
        network_mode='host', pid_mode='host', command=cmd)
    ip_addr = res.strip().decode()

    try:
        socket.inet_aton(ip_addr)
        return ip_addr
    except socket.error:
        raise ValueError('{} is not a valid ip, check docker is running')


def get_running_containers(project_name: str) -> tuple:
    """Get the number of running containers and theirs details for the current stakkr instance."""
    from requests.exceptions import ConnectionError

    filters = {
        'name': '{}_'.format(project_name),
        'status': 'running',
        'network': '{}_stakkr'.format(project_name).replace('-', '')}

    try:
        cts = get_client().containers.list(filters=filters)
    except ConnectionError:
        raise ConnectionError('Make sure docker is installed and running')

    __st__['cts_info'] = dict()
    for container in cts:
        container_info = _extract_container_info(project_name, container.id)
        __st__['cts_info'][container_info['name']] = container_info

    __st__['running_cts'] = len(cts)

    return (__st__['running_cts'], __st__['cts_info'])


def get_running_containers_name(project_name: str) -> list:
    """Get a list of compose names of running containers for the current stakkr instance."""
    cts = get_running_containers(project_name)[1]

    return sorted([ct_data['compose_name'] for docker_name, ct_data in cts.items()])


def guess_shell(container: str) -> str:
    """By searching for binaries, guess what could be the primary shell available."""
    container = get_client().containers.get(container)

    cmd = 'which -a bash sh'
    status, shells = container.exec_run(cmd, stdout=True, stderr=False)
    shells = shells.splitlines()
    if b'/bin/bash' in shells:
        return '/bin/bash'
    elif b'/bin/sh' in shells:
        return '/bin/sh'

    raise EnvironmentError('Could not find a shell for that container')


def network_exists(network: str):
    """Return True if a network exists in docker, else False."""
    try:
        get_client().networks.get(network)
        return True
    except NotFound:
        return False


def _allow_contact_subnet(project_name: str, container: str) -> None:
    status, iptables = container.exec_run(['which', 'iptables'])
    iptables = iptables.decode().strip()
    if iptables == '':
        return False

    subnet = get_subnet(project_name) + '/24'
    # Allow internal network
    try:
        container.exec_run([iptables, '-D', 'OUTPUT', '-d', subnet, '-j', 'ACCEPT'])
    finally:
        container.exec_run([iptables, '-A', 'OUTPUT', '-d', subnet, '-j', 'ACCEPT'])


def _extract_container_info(project_name: str, ct_id: str):
    """Get a hash of info about a container : name, ports, image, ip ..."""
    try:
        ct_data = get_api_client().inspect_container(ct_id)
    except NotFound:
        return None

    cts_info = {
        'id': ct_id,
        'name': ct_data['Name'].lstrip('/'),
        'compose_name': ct_data['Config']['Labels']['com.docker.compose.service'],
        'ports': _extract_host_ports(ct_data),
        'image': ct_data['Config']['Image'],
        'traefik_host': _get_traefik_host(ct_data['Config']['Labels']),
        'ip': _get_ip_from_networks(project_name, ct_data['NetworkSettings']['Networks']),
        'running': ct_data['State']['Running']
        }

    return cts_info


def _extract_host_ports(config: list):
    ports = []
    for ct_port, host_ports in config['HostConfig']['PortBindings'].items():
        ports += [host_port['HostPort'] for host_port in host_ports]

    return ports


def _get_ip_from_networks(project_name: str, networks: list):
    """Get a list of IPs for a network."""
    project_name = project_name.replace('-', '')
    network_settings = {}
    if '{}_stakkr'.format(project_name) in networks:
        network_settings = networks['{}_stakkr'.format(project_name)]

    return network_settings['IPAddress'] if 'IPAddress' in network_settings else ''


def _container_in_network(container: str, expected_network: str):
    """Return True if a container is in a network else false. Used by add_container_to_network."""
    try:
        ct_data = get_api_client().inspect_container(container)
    except NotFound:
        raise LookupError('Container {} does not seem to exist'.format(container))

    for connected_network in ct_data['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False


def _get_traefik_host(labels: list):
    if 'traefik.frontend.rule' not in labels:
        return 'No traefik rule'

    rules = labels['traefik.frontend.rule'].split(':')

    return rules[1]
