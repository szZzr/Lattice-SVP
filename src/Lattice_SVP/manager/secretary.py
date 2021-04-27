import zmq, time, janus, asyncio
from zmq.asyncio import Context as aContext

class Secretary:
    def __init__(self, requests:dict):
        self.requests = requests
        self.info = None

    async def stop_sharing(self, queue: janus.Queue):
        context = aContext()  # zmq.Context()
        self.manager = context.socket(zmq.PULL)
        self.manager.bind(self.requests['manager_stop'])
        recv = await self.manager.recv()
        if recv == b'Secretary: STOP':
            await queue.async_q.get()

    def info_gathering(self) -> bool:
        '''
        Get from the manager information for tasks

        This method implements the pattern of zmq Reply-Request.
        Ask the manager with a request for tasks information. The
        manager response with serialized information. These information
        is type of Boost1 which is a serialized dictionary, according with
        the following pattern: Boost1 = { B,M, norms, R, n }
        :return:
        '''
        context = zmq.Context()
        server_req = context.socket(zmq.REQ)
        server_req.connect(self.requests['manager'])
        server_req.send_string("I m your secretary!")
        self.info = server_req.recv()
        return True

    def info_share(self,queue: janus.Queue):
        '''
        Share Boost1-information to the workers

        This module share the information which got from the manager to the
        worker. Μanager's doesn't share itself these information to the workers
        because is waste of time, since these information still the same for each
        task. One more benefit of use a zmq-pattern of Publish-Subscribe is that at
        any time could be connect a new worker to this one Publish socket. It isn't
        necessary a worker being connected with manager at the procedure's beginning.
        :return:
        '''
        context = zmq.Context()
        publish = context.socket(zmq.PUB)
        publish.bind(self.requests['worker'])
        while not queue.sync_q.empty():
            publish.send(self.info)

    async def async_show(self, display: janus.Queue, stop: janus.Queue):
        while not stop.async_q.empty():
            data = await display.async_q.get()
            print(f"{data}")
            display.async_q.task_done()

    async def start_operation(self):
        loop = asyncio.get_event_loop()
        queue = janus.Queue()
        # display_q = janus.Queue()
        await queue.async_q.put('SHARE')
        # await display_q.async_q.put('Information sharing has begin...')

        sharing = loop.run_in_executor(None, self.info_share, queue)
        interrupt = loop.create_task(self.stop_sharing(queue))
        # display = loop.create_task(self.async_show(display_q, queue))

        await asyncio.gather(sharing, interrupt)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start_operation())
        except RuntimeError:
            print("Finish!")
        finally:
            print("JOb Finished!")
            loop.close()

def request(protocol: str, ip: str, port: int) -> str:
    return protocol + "://" + ip + ":" + str(port)


protocol = "tcp"
ip = "127.0.0.1"
ports = {'manager':8070,
         'worker': 8076,
         'manager_stop': 8079}
requests = {p:request(protocol, ip, ports[p]) for p in ports.keys()}

secretary = Secretary(requests)
if secretary.info_gathering():
    # print("Information sharing has begin...")
    secretary.run()
    print('Bye...')
    exit(0)
