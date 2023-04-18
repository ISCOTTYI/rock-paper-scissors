import asyncio
from aiohttp import web


class Player():
    def __init__(self, id, reader, writer):
        self.id = id
        self.reader = reader
        self.writer = writer
    
    async def make_move(self, game_state):
        self.writer.write(b'its your turn ' + str(game_state).encode() + b'\n')
        return int(await self.reader.readline())


class Game():
    def __init__(self):
        # TODO state is dict {player_id: (x, y)}
        # when new player joins random positions are assigned
        self.state = 1
        self.players = []
        self.max_players = 2
        def do_nothing(state):
            pass
        self.state_listener = do_nothing
    
    def notify_state_change(self): # TODO
        self.state_listener(self.state)
    
    async def handle_new_connection(self, reader, writer):
        if len(self.players) >= self.max_players:
            raise Exception(f'Already {self.max_players} players in the game!')
        player_id = len(self.players)
        self.players.append(Player(player_id, reader, writer))
        # All players joined, start game
        if len(self.players) == self.max_players:
            await self.run()
            # game = Game()
            # await game.run()
    
    async def run(self):
        whos_turn = 0
        # Game loop
        while True:
            next_player = self.players[whos_turn % 2]
            self.state = await next_player.make_move(self.state)
            self.notify_state_change()
            whos_turn += 1

    # writer.write(b'hallo')
    # data = await reader.read(100)
    # # reader.readline goes until newline character
    # message = data.decode()
    # addr = writer.get_extra_info('peername')

    # print(f"Received {message!r} from {addr!r}")

    # print(f"Send: {message!r}")
    # writer.write(data)
    # await writer.drain()

    # print("Close the connection")
    # writer.close()
    # await writer.wait_closed()

async def run_tcp_server(game):
    server = await asyncio.start_server(
        game.handle_new_connection, '127.0.0.1', 9999)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving game server on {addrs}')

    async with server:
        await server.serve_forever()


# Web server handler
async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    print('Request served!')
    return web.Response(text=text)


async def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    url = '127.0.0.1'
    port = 8080
    site = web.TCPSite(runner, url, port)
    print(f'Serving web server on {url}:{port}')
    await site.start()


async def main():
    game = Game()
    await asyncio.gather(run_tcp_server(game), run_web_server())


if __name__ == '__main__':
    asyncio.run(main())