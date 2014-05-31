import asyncio


def watch_stdin():
    msg = input('')
    return msg


class Client:
    reader = None
    writer = None

    def __init__(self):
        pass

    def send_msg(self, msg):
        msg = '{}\n'.format(msg).encode()
        assert type(msg) is bytes
        self.writer.write(msg)

    def close(self):
        print('Closing.')
        if self.writer:
            self.writer.write(b'close()\n')
        mainloop = asyncio.get_event_loop()
        mainloop.stop()

    @asyncio.coroutine
    def create_input(self):
        while True:
            mainloop = asyncio.get_event_loop()
            future = mainloop.run_in_executor(None, watch_stdin)
            input_message = yield from future
            if input_message == 'close()' or not self.writer:
                self.close()
                break
            elif input_message:
                mainloop.call_soon_threadsafe(self.send_msg, input_message)

    @asyncio.coroutine
    def connect(self):
        print('Connecting...')
        try:
            reader, writer = yield from asyncio.open_connection('127.0.0.1', 8089)
            asyncio.async(C.create_input())
            writer.write(b'Hello server!\n')
            self.reader = reader
            self.writer = writer
            while not reader.at_eof():
                msg = yield from reader.readline()
                if msg:
                    print('{}'.format(msg.decode().strip()))
            print('The server closed the connection, press <enter> to exit.')
            self.writer = None
        except ConnectionRefusedError as e:
            print('Connection refused: {}'.format(e))
            self.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    C = Client()
    connect = asyncio.async(asyncio.async(C.connect()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # Raising and going through a keyboard interrupt will not interrupt the Input
        # So, do not stop using ctrl-c, the program will deadlock waiting for watch_stdin()
        print('Got keyboard interrupt <ctrl-C>, please send "close()" to exit.')
        loop.run_forever()
    loop.close()