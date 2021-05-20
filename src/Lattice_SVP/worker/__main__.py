import zmq,asyncio, argparse
from zmq.asyncio import Context as aContext
from . import Worker

def request(protocol: str, ip: str, port: int) -> str:
    return protocol + "://" + ip + ":" + str(port)


def create_requests():
    protocol = "tcp"
    ip = "127.0.0.1"
    ports = {'pot': 8078,
             'manager': 8074,
             'secretary': 8076}
    requests = {p: request(protocol, ip, ports[p]) for p in ports.keys()}
    return requests


def async_exec(worker):
    worker.connect(aContext)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(worker.atask_assignment())
    except RuntimeError:
        print("Worker Finish!")
    finally:
        print("Worker Finish!")
        loop.close()
        print('Bye')


def exec(worker):
    worker.connect(zmq.Context)
    worker.task_assignment()

# # # RUN APPLICATION
def run(execution, threads:int=2):
    requests = create_requests()
    worker = Worker(requests, threads=threads)
    worker.info_gathering()
    print(f'---Information Received---\n'
          f'R: {worker.info["R"]} - Dimensions: {worker.info["n"]}\n')
    print('Worker is ready for process press ENTER.')
    input()
    execution(worker)


# # # TESTING APPLICATION
def testing():
    import sys
    if sys.platform == 'linux':
        print('LINUX PLATFORM')
        t_boost1 = b'\x80\x03}q\x00(X\x01\x00\x00\x00Bq\x01cnumpy.core.multiarray\n_reconstruct\nq\x02cnumpy\nndarray\nq\x03K\x00\x85q\x04C\x01bq\x05\x87q\x06Rq\x07(K\x01K\x03K\x03\x86q\x08cnumpy\ndtype\nq\tX\x02\x00\x00\x00i8q\n\x89\x88\x87q\x0bRq\x0c(K\x03X\x01\x00\x00\x00<q\rNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00tq\x0eb\x89CH\x03\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00q\x0ftq\x10bX\x01\x00\x00\x00Mq\x11h\x02h\x03K\x00\x85q\x12h\x05\x87q\x13Rq\x14(K\x01K\x03K\x03\x86q\x15h\tX\x02\x00\x00\x00f8q\x16\x89\x88\x87q\x17Rq\x18(K\x03h\rNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00tq\x19b\x89CH\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18bEi|d\xf2?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00!V\x94\xc6G&\xe0?`\xb9\xa7\x11\x96{\xea?\x00\x00\x00\x00\x00\x00\xf0?q\x1atq\x1bbX\x05\x00\x00\x00normsq\x1ch\x02h\x03K\x00\x85q\x1dh\x05\x87q\x1eRq\x1f(K\x01K\x03\x85q h\x18\x89C\x18\x91\xaf\x98\x0e\xeaA-@p\xc4\x9d9\x8dv\x1e@\xde4\xda\xfeNN*@q!tq"bX\x01\x00\x00\x00Rq#G@"\x00\x00\x00\x00\x00\x00X\x01\x00\x00\x00nq$K\x03u.'
        t_boost2 = [b'22 serialization::archive 15 0 0 1 3 0 0 0 2',
                    b'22 serialization::archive 15 0 0 0 3 0 0 1 1',
                    b'22 serialization::archive 15 0 0 0 3 0 1 1 1']
    elif sys.platform in ('darwin','unix'):
        t_boost1 = b'\x80\x03}q\x00(X\x01\x00\x00\x00Bq\x01cnumpy.core.multiarray\n_reconstruct\nq\x02cnumpy\nndarray\nq\x03K\x00\x85q\x04C\x01bq\x05\x87q\x06Rq\x07(K\x01K\x03K\x03\x86q\x08cnumpy\ndtype\nq\tX\x02\x00\x00\x00i8q\n\x89\x88\x87q\x0bRq\x0c(K\x03X\x01\x00\x00\x00<q\rNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00tq\x0eb\x89CH\x03\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00q\x0ftq\x10bX\x01\x00\x00\x00Mq\x11h\x02h\x03K\x00\x85q\x12h\x05\x87q\x13Rq\x14(K\x01K\x03K\x03\x86q\x15h\tX\x02\x00\x00\x00f8q\x16\x89\x88\x87q\x17Rq\x18(K\x03h\rNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00tq\x19b\x89CH\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18bEi|d\xf2?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00!V\x94\xc6G&\xe0?`\xb9\xa7\x11\x96{\xea?\x00\x00\x00\x00\x00\x00\xf0?q\x1atq\x1bbX\x05\x00\x00\x00normsq\x1ch\x02h\x03K\x00\x85q\x1dh\x05\x87q\x1eRq\x1f(K\x01K\x03\x85q h\x18\x89C\x18\x91\xaf\x98\x0e\xeaA-@p\xc4\x9d9\x8dv\x1e@\xde4\xda\xfeNN*@q!tq"bX\x01\x00\x00\x00Rq#G@"\x00\x00\x00\x00\x00\x00X\x01\x00\x00\x00nq$K\x03u.'
        t_boost2 = [b'22 serialization::archive 17 0 0 1 3 0 0 0 2',
                    b'22 serialization::archive 17 0 0 0 3 0 0 1 1',
                    b'22 serialization::archive 17 0 0 0 3 0 1 1 1']
    requests = create_requests()
    test_worker = Worker(requests,threads=2)
    test_worker.test(t_boost1,t_boost2)

def set_options():
    parser = argparse.ArgumentParser(prog="Worker",
                                     usage='%(prog)s [options] commands',
                                     description="Worker-module which based on Schnorr and "
                                                 "Euchner algorithm, executes the given task.")
    parser.add_argument('-D', '--debug',
                        help="Debug mode, defines the worker to run on the simulator. This mode"
                             "applies asynchronous communication, uses python's asyncio library.",
                        action="store_true",
                        dest="debug")
    parser.add_argument('-T', '--threads',
                        help="Testing mode, sets up the worker to run with predefined data. This "
                             "mode is just for testing usage, to note if the worker has normally "
                             "execution.",
                        action="store",
                        type = int,
                        dest="threads",
                        default=2),
    parser.add_argument('-t', '--testing',
                        help="Testing mode, sets up the worker to run with predefined data. This "
                             "mode is just for testing usage, to note if the worker has normally "
                             "execution.",
                        action="store_true",
                        dest="testing")
    return parser.parse_args()

def main(options):
    if options.debug:
        run(async_exec, options.threads)
    elif options.testing:
        testing()
    else:
        run(exec, options.threads)
    return


if __name__[-8:]=="__main__":
    exit(main(set_options()))
elif __name__=="Lattice_SVP.worker.worker":
    options = set_options()
    if not options.testing:
        print('TIP: For worker testing just use the flag -T.')
    exit(main(options))
else:
    print(f'FAILED INITILIAZATION!!!\nname: {__name__}')
