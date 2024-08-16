import socket as soc
from socket import socket
import select

from weather_service import OpenmeteoParcer
from coordinates_service import GetCoordinates


class Server:
    __tasks = []
    __inputs = {}
    __outputs = {}

    def __init__(self, host: str, port: int) -> None:
        self.server_socket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        self.server_socket.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.__tasks.append(self.__server())

        self.weather_parcer = OpenmeteoParcer()
        self.coordinates_parcer = GetCoordinates()

    def __parse_request(self, request: str):
        parsed = request.split(" ")
        method = parsed[0]
        url = parsed[1]
        return (method, url)

    def __generate_headers(self, method, url):
        if not method == "GET":
            return ("HTTP/1.1 405 Method not allowed\n\n", 405)
        if url != "/":
            return ("HTTP/1.1 404 Not fount\n\n", 404)

        return ("HTTP/1.1 200 OK\n\n", 200)

    def __generate_content(self, code, ip_address):
        if code == 404:
            return "<h1>404</h1><p>Not fount</p>"
        if code == 405:
            return "<h1>405</h1><p>Method not allowed</p>"

        coordinates = self.coordinates_parcer.get_coordinates(ip_address)
        weather = self.weather_parcer.get_weather(coordinates)
        return "<h1>it's {} degrees Celsius in {} now.</h1>".format(
            weather.temperature, weather.city
        )

    def __generate_response(self, request, ip_address):
        method, url = self.__parse_request(request)
        headers, code = self.__generate_headers(method, url)
        body = self.__generate_content(code, ip_address)
        return (headers + body).encode()

    def __server(self):
        while True:
            yield ("read", self.server_socket)
            client_socket, addr = self.server_socket.accept()
            self.__tasks.append(self.__client(client_socket, addr))

    def __client(self, client_socket: socket, addr):
        while True:
            yield ("read", client_socket)
            request = client_socket.recv(1024)
            print("{} : {}".format(client_socket.getpeername(), request))

            if not request:
                break
            else:
                response = self.__generate_response(request.decode("utf-8"), addr[0])

                yield ("write", client_socket)
                client_socket.send(response)

        client_socket.close()

    def event_loop(self):
        while any([self.__tasks, self.__inputs, self.__outputs]):
            while not self.__tasks:
                ready_inputs, ready_outputs, _ = select.select(
                    self.__inputs.keys(), self.__outputs.keys(), [], 0.5
                )

                for sock in ready_inputs:
                    self.__tasks.append(self.__inputs.pop(sock))
                for sock in ready_outputs:
                    self.__tasks.append(self.__outputs.pop(sock))

            try:
                task = self.__tasks.pop(0)
                method, sock = next(task)

                if method == "read":
                    self.__inputs[sock] = task
                elif method == "write":
                    self.__outputs[sock] = task

            except StopIteration:
                pass
