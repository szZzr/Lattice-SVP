import argparse
from . import Manager, cur_path

def path_handler(path:str=cur_path, prev_dir:int=1):
    dirs = path.split('/')
    data_path = ''
    for dir in dirs[1:-prev_dir]:
        data_path += '/' + dir
    return data_path

def request(port:int) -> str: #protocol: str, ip:str,
    '''
    Create request for zmq framework.
    :param protocol: transport protocol: "tcp" | "udp"
    :param ip: The ip address where the request will send
    :param port:
    :return: str "protocol://ip:port"
    '''
    protocol = "tcp"
    ip = "127.0.0.1"
    return protocol + "://" + ip + ":" + str(port)


def run(requests: dict, mode:int, request:int, path:str, settings:dict):
    '''
    Setting up manager.
    mode:       0 -> CONDITION.VIA_DEPTH
                1 -> CONDITION.VIA_NODES

    request:    VIA_DEPTH -> denotes depth of tree
                VIA_NODES -> denotes number of requested tasks
    :param requests:
    :return:
    '''
    Manager.data_path = path
    manager = Manager(requests)
    manager.division_of_labour(mode= mode, request=request, settings = settings)
    if settings['basis'] == 'test' and not settings['simulate']:
        manager.show_serial_tasks()
        return

    if manager.inform_secretary():
        manager.share_tasks()
        manager.term_secretary()
        manager.context_term()
    else:
        print("Didn't find secretary...")

def set_options():
    parser = argparse.ArgumentParser(
        prog="Manager",
        usage='%(prog)s [options] commands',
        description="Server-module which splits and shares tasks to "
                    "workers in order to solve the SVP.",
        epilog="Good Luck!")
    ports = {'secretary': 8070,
             'pot': 8072,
             'worker': 8074}
    settings = {
        'dimensions':50,'bits':63, 'blocksize':20
    }
    parser.add_argument('-w', '--worker',
                        help="Manager's port to communicate with workers.",
                        action="store",
                        type=int,
                        dest="worker",
                        default=ports['worker'])
    parser.add_argument('-s', '--secretary',
                        help="Manager's port to communicate with secretary.",
                        action="store",
                        type=int,
                        dest="secretary",
                        default=ports['secretary'])
    parser.add_argument('-p', '--pot',
                        help="Manager's port to communicate with pot.",
                        action="store",
                        type=int,
                        dest="pot",
                        default=ports['pot'])
    parser.add_argument('-D', '--depth',
                        help="Set mode VIA_DEPTH and define the desired depth for"
                             " enumeration tree. Suppose that root's height equals"
                             " to zero.",
                        action="store",
                        type=int,
                        dest="depth",
                        default=-1)
    parser.add_argument('-N', '--nodes',
                        help="Set mode VIA_NODES and define the number of nodes-tasks"
                             "according to which you prefer to split the job.",
                        action="store",
                        type=int,
                        dest="nodes",
                        default=-1)
    parser.add_argument('-B', '--basis',
                        help="Set basis. The default mode is random calculating basis,"
                             "according with optional settings below (dimensions, bits "
                             "and blocksize). You can set a predefined basis, or set a "
                             "test basis just to verify that module works right.",
                        action="store",
                        type=str,
                        dest="basis",
                        default="random")
    parser.add_argument('-T', '--testing',
                        help="Testing mode, sets up the worker to run with predefined data. This "
                             "mode is just for testing usage, to note if the worker has normally "
                             "execution.",
                        action="store_true",
                        dest="testing")
    parser.add_argument('-R',
                        help="Set R, range manually. It doesn't recommend to use "
                             "this option.",
                        action="store",
                        type=float,
                        dest="R",
                        default=-1)
    parser.add_argument('-d', '--dimensions',
                        help="Dimensions.",
                        action="store",
                        type=int,
                        dest="dimensions",
                        default=settings['dimensions'])
    parser.add_argument('-b', '--bits',
                        help="Bits.",
                        action="store",
                        type=int,
                        dest="bits",
                        default=settings['bits'])
    parser.add_argument('-bs', '--blocksize',
                        help="Blocksize.",
                        action="store",
                        type=int,
                        dest="blocksize",
                        default=settings['blocksize'])
    parser.add_argument('--simulate',
                        help="Simulate mode, defines the worker to run on the simulator",
                        action="store_true",
                        dest="simulate")
    return parser.parse_args()

def main(path:str):
    '''
    mode:   0 -> CONDITION.VIA_DEPTH
            1 -> CONDITION.VIA_NODES
    :param options: argparse options
    :return:
    '''
    options = set_options()
    ports = {
        'secretary': options.secretary,
        'secretary_stop': 8079,
        'pot': options.pot,
        'worker': options.worker
    }
    requests = {p: request(ports[p]) for p in ports.keys()}
    settings = {
        'simulate': options.simulate, #run via simulator
        'basis':'test' if options.testing else options.basis,
        'R':options.R,
        'dimensions': options.dimensions,
        'bits': options.bits,
        'blocksize': options.blocksize
    }
    # NOTE: by default options.EACH_MODE is -1.
    if options.depth > options.nodes:
        # VIA_DEPTH
        run(requests, 0, options.depth, path, settings)
    else:
        # VIA_NODES
        run(requests, 1, options.nodes, path, settings)
    print('Jobs has Finished!')
    exit(0)


if __name__=="__main__":
    path = path_handler(path = cur_path, prev_dir = 1) + '/data'
    main(path)
elif __name__=="manager":
    print('CALL LIKE MODULE')
elif __name__=="Lattice_SVP.manager.__main__":
    import os,sys
    cur_path = os.getcwd()
    print(f"Path: {cur_path}")
    sys.path.append(cur_path)
    main(cur_path + '/src/data')
    # run_manager()
