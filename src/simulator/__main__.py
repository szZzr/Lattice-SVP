from . import *

def close_ports():
    '''
        This method close all open ports which are used by the application.
        It requires to run the application as system administrator using the
        sudo keyword.
        :return: List with terminated pids.
        '''
    conns = psutil.net_connections()
    pids = []
    for conn in conns:
        if conn.laddr.port in range(8070,8083):
            pids.append(conn.pid)
    pids = list(dict.fromkeys(pids))
    if len(pids) == 0:
        print("\t----Ports are already closed----")
        return False
    else:
        print(f"Pids to terminate {pids}.")
    for pid in pids:
        try:
            psutil.Process(pid).terminate()
            pids.append(pid)
        except psutil.NoSuchProcess:
            print(f'Process[{pid}] is already terminated.')
    print("\t----Ports just closed----")
    return True

def run(options):
    print(f'MAIN THREAD: {threading.current_thread() is threading.main_thread()}')
    if sys.platform in ('darwin','unix') :
        if options.close_ports:
            close_ports()

        executor = Executor(options)
        print(f'path: {Executor.PATH}')
        cw = asyncio.get_child_watcher()
        loop = asyncio.get_event_loop()
        asyncio.get_child_watcher()
        try:
            loop.run_until_complete(executor.run(timeout=options.timeout))
            # loop.run_forever()
        except RuntimeError:
            print("Finish!")
        finally:
            loop.run_until_complete(executor.close())
            cw.close()
            loop.close()
            print('Application has Terminated...')


def set_options():
    parser = argparse.ArgumentParser(prog="simulator",
                                     usage='%(prog)s [options] commands',
                                     description="Simulation of distributed and parallel algorithm of Schnorr and Euchner",
                                     epilog="Good Luck!")
    _options = {'workers': 3,
                'ports': 8070,  # list(range(8070,8080,2))
                'threads': 2,
                'timeout': 20,
                'dimensions': 50, 'bits': 63, 'blocksize': 25}
    parser.add_argument('-c', '--close_ports',
                        help="Just close all ports used by current application. To set this module must you"
                             "run the application as administrator, so that to allow the application to have"
                             "access to your system ports. To run as administrator use the keyword sudo."
                             "After that you can safely run the application without sudo and -c flag.",
                        action="store_true",
                        dest="close_ports")
    parser.add_argument('-W', '--workers',
                        help="Number of workers.",
                        action="store",
                        type=int,
                        dest="workers",
                        default=_options['workers'])
    parser.add_argument('-P', '--ports',
                        help="Starting value of port. You should notice that this value determines the first port of a total"
                             "range of 5 ports. For example, if you give as input -p 8070, it will bind the ports 8070-8078,"
                             " this ports as well are the default ports.",
                        action="store",
                        type=int,
                        dest="ports",
                        default=_options['ports'])
    parser.add_argument('-T', '--threads',
                        help="Threads for each process.",
                        action="store",
                        type=int,
                        dest="threads",
                        default=_options['threads'])
    parser.add_argument('-D', '--depth',
                        help="Set MANAGER mode as VIA_DEPTH and define the desired depth for"
                             " enumeration tree. Suppose that root's height equals"
                             " to zero.",
                        action="store",
                        type=int,
                        dest="depth",
                        default=-1)
    parser.add_argument('-N', '--nodes',
                        help="Set MANAGER mode as VIA_NODES and define the number of nodes-tasks"
                             "according to which you prefer to split the job.",
                        action="store",
                        type=int,
                        dest="nodes",
                        default=-1)
    parser.add_argument('-B', '--basis',
                        help="Set basis. The default mode is random calculation of basis, "
                             "according with optional settings below (dimensions, bits "
                             "and blocksize). You can set a predefined basis, or set a "
                             "test basis just to verify that module works fine. To execute in "
                             "test mode just use the flag \'-B test\'.",
                        action="store",
                        type=str,
                        dest="basis",
                        default="random")
    parser.add_argument('-R',
                        help="Set R, range manually. It doesn't recommend to use "
                             "this option.",
                        action="store",
                        type=float,
                        dest="R",
                        default=-1)
    parser.add_argument('-to', '--timeout',
                        help="Set timeout",
                        action="store",
                        type=int,
                        dest="timeout",
                        default=_options['timeout'])
    parser.add_argument('-d', '--dimensions',
                        help="Dimensions.",
                        action="store",
                        type=int,
                        dest="dimensions",
                        default=_options['dimensions'])
    parser.add_argument('-b', '--bits',
                        help="Bits.",
                        action="store",
                        type=int,
                        dest="bits",
                        default=_options['bits'])
    parser.add_argument('-bs', '--blocksize',
                        help="Blocksize.",
                        action="store",
                        type=int,
                        dest="blocksize",
                        default=_options['blocksize'])
    return  parser.parse_args()


def main():
    options = set_options()
    print(options)
    if options.close_ports:
        close_ports()
    else:
        run(options)


smain = '__main__'
if __name__== smain or __name__[len(smain):]==smain:
    print('FIRST HERE')
    main()
elif __name__=="app":
    options = {'close_ports':False, 'workers':2}
    run(options)
