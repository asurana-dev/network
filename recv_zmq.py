import time
import zmq
import subprocess
import os
import stat

commands = []
POLL_TIMEOUT = 5

def run_commands():
    global commands

    commands, executing = [], commands
    start_time = time.time()

    processes = []
    for command in executing:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        processes.append((proc, command))

    print 'Waiting for', len(executing), 'commands to complete.'

    results = []
    for proc, command in processes:
        out, error = proc.communicate()
        results.append(dict(output=out, error=error, command=command))

    return dict(start=start_time, end=time.time(), results=results)


def create_shell_script(cmds):

    homefolder = os.path.expanduser('~')
    if 'run' in cmds[0]:
        script_file = os.path.abspath('%s/docker.sh' % homefolder)
    else:
        script_file = os.path.abspath('%s/links.sh' % homefolder)

    fn = open(script_file, 'w')
    fn.write(cmds[0])
    fn.close()

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)


def create_netns(cmds):

    global commands

    params = cmds[0]

    if params['role'] == 'leaf':
        for i in range(params['start_rack_id'], params['end_rack_id']):
            for j in range(1, params['nLeafs']+1):
                commands = ["docker inspect -f '{{.State.Pid}}' %d-%d" % (i, j)] 
                out = run_commands()
                pid = out['results'][0]['output'].strip()
                commands = ['ln -s /proc/%s/ns/net /var/run/netns/%d-%d' % (pid, i, j)] 
                out = run_commands()
    else:
        for i in range(params['start_spine_id'], params['end_spine_id']):
            commands = ["docker inspect -f '{{.State.Pid}}' 0-%d" % (i)]
            out = run_commands()
            pid = out['results'][0]['output'].strip()
            commands = ['ln -s /proc/%s/ns/net /var/run/netns/0-%d' % (pid, i)]
            out = run_commands()

def main():
     

    context = zmq.Context()

    poll = zmq.Poller()

    ucast_socket = context.socket(zmq.REP)
    ucast_socket.bind("tcp://*:90")

    #mcast_socket = context.socket(zmq.SUB)
    #mcast_socket.setsockopt(zmq.SUBSCRIBE, '')
    #mcast_socket.bind("tcp://*:91")

    file_socket = context.socket(zmq.REP)
    file_socket.bind("tcp://*:92")

    poll.register(ucast_socket, zmq.POLLIN)
    #poll.register(mcast_socket, zmq.POLLIN)
    poll.register(file_socket, zmq.POLLIN)

    while True:
        socks = dict(poll.poll(POLL_TIMEOUT))
        if socks.get(file_socket) == zmq.POLLIN:
            cmds = file_socket.recv_json()
            for cmd in cmds:
                if 'docker' in cmds[0] or 'netns' in cmds[0]:
                    create_shell_script(cmds)    
                else:
                    create_netns(cmds)

                file_socket.send_string('done')

        if socks.get(ucast_socket) == zmq.POLLIN:
            cmds = ucast_socket.recv_json()
            for command in cmds:
                commands.append(command)
            output = run_commands()
            ucast_socket.send_json(output)

        #if socks.get(mcast_socket) == zmq.POLLIN:
        #    mcast_cmd = mcast_socket.recv_string()
        #    if mcast_cmd == 'begin' and commands:
        #        output = run_commands()
        #        ucast_socket.send_json(output)

if __name__ == '__main__':
    main()

