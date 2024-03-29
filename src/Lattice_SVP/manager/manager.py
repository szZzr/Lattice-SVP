from . import num, numf
from .sup_libs import *
from .std_libs import *
from .manager_process import ManagerProcess


class Manager:
    data_path = ''
    def  __init__(self, requests:dict):
        self.requests = requests
        self.tasks = {}
        self.context = zmq.Context()
        self.R = None

    def to_ndarray(self, integerMatrix: IntegerMatrix, dtype:type) -> np.ndarray:
        '''
        Converts an IntegerMatrix to ndarray
        :param integerMatrix: A 2d-matrix
        :type integerMatrix: IntegerMatrix
        :param dtype: Desired type of returning array
        :type dtype: type
        :return: ndarray
        '''
        return np.array(list(integerMatrix), dtype=dtype)

    def test_basis(self):
        b1 = [[3, 11, 12], [6, 3, 12], [13, 15, 0]]
        b2 = [[3, 6, 13], [11, 3, 15], [12, 12, 0]]
        basis = IntegerMatrix.from_matrix(b2)
        R = 9
        return basis, R

    def best_norm(self, basis):
        from numpy.linalg import norm
        l_basis = list(basis)
        l_basis.sort(key=lambda lb: norm(lb))
        it = iter(l_basis)
        best = next(it)
        while norm(best) == 0:
            best = next(it)
        return norm(best)*1.01

    def random_basis(self, dimensions, bits, blocksize):
        path = Manager.data_path + '/basis/random'
        print(f'The path: {path}')
        #basis = bkz(copy(c_basis(dimensions, bits)), block_size=blocksize)
        random_basis = c_basis(dimensions, bits)
        basis = lll(copy(random_basis))
        # bkz_basis = bkz(copy(random_basis), block_size=dimensions//2)
        R = float(gh(basis, 1.05))
        with open( path, 'wb') as file:
            pkl.dump({'basis': random_basis, 'lll_basis':basis, 'R':R, 'n':dimensions},file)
        b_norm = self.best_norm(basis)
        print('GH: ', R, " BestNorm: ",b_norm)
        if (b_norm > R):
            b_norm = R
        return basis, b_norm

    def predefined_basis(self, data_path:str = None):
        path = '/basis/random' if data_path is None else data_path
        print("path: ", Manager.data_path+path)
        with open(Manager.data_path+path, 'rb') as file:
            _, basis, R, _ = pkl.load(file).values()
        return basis, R

    def division_of_labour(self, mode: int, request: int, settings: dict):
        '''
        Divide in tasks the enumeration procedure.

        This method defines Basis of a Lattice using a random algorithm to
        produce the lattice according with the SVP Competition and subsequently
        invokes cython's ManagerProcess module which divide the main task in
        subtasks. The cython's module result is already serialized. The type of
        cython result "tasks" is a dictionary with the following pattern
        {'boost1': b_infos, 'boost2': b_jobs}
        where Boost1: ( B,M, norms, R, n ) and Boost2: ( x,limit )
        :param no_tasks: an integer which defines the number of task which
        select to divide the whole work
        :type no_tasks: int
        :return: A dictionary {'boost1': b_infos, 'boost2': b_jobs} has
        explained above
        '''
        settings['basis'] = settings['basis'].strip()
        if settings['basis'] == 'test':
            basis, self.R = self.test_basis()
        elif settings['basis'] == 'random':
            basis, self.R = self.random_basis(dimensions=settings['dimensions'],
                                         bits=settings['bits'],
                                         blocksize=settings['blocksize'])
        else:
            basis, self.R = self.predefined_basis(settings['basis'])
        nd_basis = self.to_ndarray(basis, num)

        # print(settings['R'])
        if not (settings['R'] == -1):
            self.R = settings['R']

        print("R: ", self.R)

        try:
            s = time.time()
            self.tasks = ManagerProcess.algorithm(nd_basis, self.R, mode, request)
            duration = time.time() - s
            print("Duration: ", duration)
        except OverflowError:
            exit('\nError: You MUST set the execution mode (tip: --help).\n')
        # s1 = time.time()
        # fp = fp_svp.shortest_vector(basis)
        # duration1 = time.time() - s1
        # print("FPYLLL: ", np.linalg.norm(fp), "\tTIME: ", duration1)

    def inform_secretary(self) -> bool:
        '''
        Sends information about the procedure to secretary-node.

        This method uses the zmq framework to communicate with a node, which
        represents manager's secretary. It implements the Request-Reply pattern,
        first the secretary node ask the manager for the usefull informations
        after confirms that this method is the secretary node and responses
        sending the following infos.
        Boost1: ( B,M, norms, R, n )
        :return: True if communication has established and completed
        '''
        secretary = self.context.socket(zmq.REP)
        try:
            secretary.bind(self.requests['secretary'])
        except zmq.error.ZMQError:
            self.address_in_use_Ex('secretary')

        while True:  # not(informed)
            request = secretary.recv_string()
            if request == "I m your secretary!":
                secretary.send(self.tasks['boost1'])
                print("Secretary has informed!\n")
                break
        secretary.close()
        return True

    def term_secretary(self) -> bool:
        # context = aContext()
        secretary = self.context.socket(zmq.PUSH)
        secretary.connect(self.requests['secretary_stop'])
        secretary.send(b'Secretary: STOP')
        secretary.close()
        print("Secretary has closed.")
        return True

    def share_tasks(self) -> bool:
        '''
        Sending tasks to the workers Implements zmq's pipeline pattern s

        According with zmq pipeline pattern, it implements the communication
        between manager and workers. First established the communication with
        the worker-port where will send each task and the candidates workers
        could grap them. Secondly established the connection between the
        pot-port. Finally sends each task of the list to the worker's port.
        '''
        # context = zmq.Context()
        connections = {'worker':None, 'pot':None}
        import time
        for conn in connections.keys():
            connections[conn] = self.context.socket(zmq.PUSH)
        #self.socket_communicate(lambda req: connections[conn].bind(req),'worker')
        #self.socket_communicate(lambda req: connections[conn].connect(req),'pot')
            try:
                print(f'\tTry to open {conn}\'s port...{self.requests[conn]}')
                if conn=='worker':
                    connections[conn].bind(self.requests[conn])
                else:
                    connections[conn].connect(self.requests[conn])
            except zmq.error.ZMQError:
                self.address_in_use_Ex(conn)
            finally:
                print(f'\t...{conn}\'s port is open!\n')

        print('Press ENTER if workers are ready')
        input()
        # self.stop_secretary()


        len_tasks = len(self.tasks['boost2'])
        connections['pot'].send_string(hex(len_tasks))
        connections['pot'].send_string(float(self.R).hex())

        # worker.send(tasks['boost1'])
        for i, task in enumerate(self.tasks['boost2']):
            connections['worker'].send(task)
            print("The task-" + str(i) + " has been sent!")
        connections['worker'].close()
        connections['pot'].close()
        return True

    def socket_communicate(self, zmq_method, port):
        try:
            print(f'\tTry to open {port}\'s port...{self.requests[port]}')
            zmq_method(self.requests[port])
        except zmq.error.ZMQError:
            '''Message Error for address in use zmq Exception.'''
            print(f'\n---FAILED---')
            print(f'{port.capitalize()}-Communication-Port is in use.\n'
                f'The request {self.requests[port]} has failed.')
            print(f'\nTIP: You can use command: \'simulator -c\'')
            exit(-1)
        finally:
            print(f'\t...{port}\'s port is open!\n')

    def address_in_use_Ex(self,connection:str):
        '''Message Error for address in use zmq Exception.'''
        print(f'\n---FAILED---')
        print(f'{connection.capitalize()}-Communication-Port is in use.\n'
            f'The request {self.requests[connection]} has failed.')
        print(f'\nTIP: You can use command: \'simulator -c\'')
        exit(-1)

    def context_term(self):
        self.context.term()
        print("Terminate Connections")

    def show_serial_tasks(self):
        print(f'--Secretary Information---\n{self.tasks["boost1"]}\n\n---Tasks---\n')
        for i, task in enumerate(self.tasks['boost2']):
            print(f'{i}) {task}')




# port_secretary = "8070"
# port_pot = "8072"
# port_worker = "8074"
# tasks = tasks4share(no_tasks=4)
# # print(tasks['boost1'])
# # print(tasks['boost2'])
# # input('0-> To inform the secretary ENTER')
# inform_secretary(tasks['boost1'],
#                  address=request(protocol,ip,port_secretary))
#
# input('1-> To start sharing press ENTER')
# manager(tasks['boost2'],
#         pot_addr=request(protocol, ip, port_pot),
#         worker_addr=request(protocol, ip, port_worker))
