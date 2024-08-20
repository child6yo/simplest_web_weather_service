import socket as soc
from socket import socket
import select

from weather_service import OpenmeteoParcer, Coordinates


class Server:
    _tasks = []
    _inputs = {}
    _outputs = {}

    content = None

    def __init__(self, host: str, port: int) -> None:
        self.server_socket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        self.server_socket.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        self.weather_service = OpenmeteoParcer()

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

    def __generate_content(self, code):
        if code == 404:
            return "<h1>404</h1><p>Not fount</p>"
        if code == 405:
            return "<h1>405</h1><p>Method not allowed</p>"

        current_weather = self.weather_service.get_weather(
            Coordinates(latitude=53.36056, longtitude=83.76361)
        )
        return "<h1>it's {} degrees Celsius in Barnaul now.</h1>".format(current_weather.temperature)

    def __generate_response(self, request):
        method, url = self.__parse_request(request)
        headers, code = self.__generate_headers(method, url)
        body = self.__generate_content(code)
        return (headers + body).encode()

    def _server(self):
        while True:
            yield ("read", self.server_socket)
            client_socket, addr = self.server_socket.accept()
            self._tasks.append(self.__client(client_socket))

    def __client(self, client_socket: socket):
        while True:
            yield ("read", client_socket)
            request = client_socket.recv(1024)
            print("{} : {}".format(client_socket.getpeername(), request))

            if not request:
                break
            else:
                response = self.__generate_response(request.decode("utf-8"))

                yield ("write", client_socket)
                client_socket.send(response)

        client_socket.close()
