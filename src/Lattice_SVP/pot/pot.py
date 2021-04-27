import zmq, time, pickle as pkl
from numpy.linalg import norm
# from zmq.asyncio import Context as aContext

class Pot():
    def __init__(self, m_address:str, w_address:str):
        context = zmq.Context()
        self.manager = context.socket(zmq.PULL)
        self.manager.bind(m_address)

        # acontext = aContext()
        self.workers = context.socket(zmq.PULL)
        self.workers.bind(w_address)

        self.no_tasks = 0
        self.results = []

    def manager_conn(self):
        self.no_tasks = int(self.manager.recv(), 16)
        R = float.fromhex(self.manager.recv().decode("utf-8"))
        # R = 1
        print(f"The number of tasks are {self.no_tasks}, recommended R is {R}")
        print("\t...procedure begins!")
        self.manager.close()

    def workers_conn(self):
        for task in range(self.no_tasks):
            worker = self.workers.recv()
            result = pkl.loads(worker)
            self.results += result
            print(result)
        self.workers.close()

    def best_norm(self):
        self.results.sort(key=lambda result: norm(result))
        it = iter(self.results)
        best = next(it)
        while norm(best) == 0:
            best = next(it)
        return norm(best)

    def run(self):
        self.manager_conn()

        tstart = time.time()
        self.workers_conn()
        tend = time.time()

        print("Total Time: ", (tend - tstart) * 1000)

        if len(self.results) == 0:
            print("No Solution!")
            return
        return self.best_norm()
