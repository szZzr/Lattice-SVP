import zmq,asyncio, argparse, pickle as pkl
from numpy.linalg import norm
from zmq.asyncio import Context as aContext
from worker_process import WorkerProcess

class Worker:
    def __init__(self, requests: dict, threads: int):
        self.requests = requests
        self.threads = threads
        self.info = {}
        self.m_connect = None # connect to manager
        self.p_connect = None # connect to pot

        self.semaphore = asyncio.Semaphore()

    def info_gathering(self):
        '''
        Collect information for the task's procedure

        This method implements the Publish-Subscribe pattern of
        zmq, according with that connects with manager's secretary
        node which one is a publisher, and subscribes information about
        following task processing. The information includes a dictionary
        with the following details
        Boost1: ( B,M, norms, R, n )
        these details equiped the processing method which follows.
        :return:
        '''
        context = zmq.Context()
        info_channel = context.socket(zmq.SUB)
        info_channel.connect(self.requests['secretary'])
        info_channel.setsockopt_string(zmq.SUBSCRIBE, '')
        self.info = pkl.loads(info_channel.recv())

    def task_processing(self, task: bytes) -> bytes:
        '''
        Enumeration procedure to find the SVP.

        This method invokes the core of the Schnorr and Euchner
        algorithm. The enumeration algorithm has implemented in
        cython module using parallel processing this module setting
        up in the present method.
        :param task: Serialized task's parameters
        :type task: bytes
        :return:
        '''
        result = WorkerProcess.intro(self.threads,
                                     self.info['B'],
                                     self.info['M'],
                                     self.info['norms'],
                                     self.info['R'],
                                     self.info['n'],
                                     boost2=task)
        return result

    def connect(self, Context):
        context = Context() # zmq.Context()
        self.m_connect  = context.socket(zmq.PULL)
        self.m_connect.connect(self.requests['manager'])
        self.p_connect = context.socket(zmq.PUSH)
        self.p_connect.connect(self.requests['pot'])

    async def receive(self):
        await self.semaphore.acquire()
        atask = await self.m_connect.recv()
        print('I RECEIVED')
        self.semaphore.release()
        return atask

    async def atask_assignment(self):
        '''
        Collects tasks and sends the results to pot

        First of all this method established the communication
        between worker-manager and worker-pot according with zmq
        pattern pipeline. After all gets each task from the manager
        accomplish each one and set the results to the pot, this
        procedure repeated infinitely.
        '''
        try:
            # loop = asyncio.get_event_loop()
            id = 1
            while True:
                atask = await asyncio.wait_for(self.m_connect.recv(), timeout=0.1)
                print(f"{''.join(['-' for i in range(30)])}")
                print(f"Task-{id} has received.")
                result = self.task_processing(atask)
                # result = loop.run_in_executor(None, self.task_processing, atask)
                await self.p_connect.send(result)
                print(f'--|Result: {pkl.loads(result)}' )
                print(f"{''.join(['-' for i in range(30)])}\n")
                id += 1
                # atask = await asyncio.wait_for(self.m_connect.recv(), timeout=1)
                print('Next job press Enter')
                input()
        except asyncio.TimeoutError:
            print("--- No more tasks! ---")

    def task_assignment(self):
        '''
        Collects tasks and sends the results to pot

        First of all this method established the communication
        between worker-manager and worker-pot according with zmq
        pattern pipeline. After all gets each task from the manager
        accomplish each one and set the results to the pot, this
        procedure repeated infinitely.
        '''
        id = 1
        while True:
            task = self.m_connect.recv()
            print(f"{''.join(['-' for i in range(30)])}")
            print(f"Task-{id} has received.")
            result = self.task_processing(task)
            self.p_connect.send(result)
            print(f'--|Result: {pkl.loads(result)}' )
            print(f"{''.join(['-' for i in range(30)])}\n")
            id += 1

    def test(self, boost1: bytes, boost2: list):
        """
        Testing module with standard inputs

        This method just test the cython module WorkerProcess
        given the standard serialized inputs.
        :param boost1: Serialize dictionary with these data ( B,M, norms, R, n )
        :type boost1: bytes
        :param boost2: A list with serialized tasks
        :type boost2: list
        :return:
        """
        self.info = pkl.loads(boost1)
        results = []
        for i, b2 in enumerate(boost2):
            print("\n--- Task", i + 1, "---")
            result = self.task_processing(b2)
            results += pkl.loads(result)
            print("\nThe reuslt: ", result,"\n\n")

        results.sort(key=lambda lb: norm(lb))
        it = iter(results)
        best = next(it)
        while norm(best) == 0:
            best = next(it)
        print("\n\n===Results===\n", results)
        print("\n\nThe best one: ", norm(best))
        return norm(best)


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
def run(execution):
    requests = create_requests()
    worker = Worker(requests, threads=2)
    worker.info_gathering()
    print(f'---Information Received---\n'
          f'R: {worker.info["R"]} - Dimensions: {worker.info["n"]}\n')
    print('Worker is ready for process press ENTER.')
    input()
    execution(worker)


# # # TESTING APPLICATION
def testing():
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
                        help="Debuge mode, defines the worker to run on the simulator. This mode"
                             "applies asynchronous communication, uses python's asyncio library.",
                        action="store_true",
                        dest="debug")
    parser.add_argument('-T', '--testing',
                        help="Testing mode, sets up the worker to run with predefined data. This "
                             "mode is just for testing usage, to note if the worker has normally "
                             "execution.",
                        action="store_true",
                        dest="testing")
    return parser.parse_args()

def main(options):
    if options.testing:
        testing()
    elif options.debug:
        run(async_exec)
    else:
        run(exec)
    exit(0)


if __name__=="__main__":
    main(set_options())
elif __name__=="Lattice_SVP.worker.worker":
    options = set_options()
    if not options.testing:
        print('TIP: For worker testing just use the flag -T.')
    main(options)
