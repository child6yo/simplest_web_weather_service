from server import Server
from config_data import config
import select

server = Server(config.HOST, config.PORT)
server._tasks.append(server._server())

def event_loop():
    while any([server._tasks, server._inputs, server._outputs]):
        while not server._tasks:
            ready_inputs, ready_outputs, _ = select.select(
                server._inputs.keys(), server._outputs.keys(), [], 0.5
            )

            for sock in ready_inputs:
                server._tasks.append(server._inputs.pop(sock))
            for sock in ready_outputs:
                server._tasks.append(server._outputs.pop(sock))

        try:
            task = server._tasks.pop(0)
            method, sock = next(task)

            if method == "read":
                server._inputs[sock] = task
            elif method == "write":
                server._outputs[sock] = task

        except StopIteration:
            pass


if __name__ == "__main__":
    event_loop()
