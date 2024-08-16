from server import Server
from config_data import config


class Main:

    def __init__(self) -> None:
        server = Server(config.HOST, config.PORT)
        server.event_loop()


if __name__ == "__main__":
    Main()
