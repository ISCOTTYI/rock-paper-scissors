import asyncio
import json
from aiohttp import web
from random import randint

class Player():
    def __init__(self, id, reader, writer):
        self.id = id
        self.reader = reader
        self.writer = writer
    
    async def make_move(self, game_state):
        # TODO catch error if player disconnects, takes too long or other shit
        # TODO deal with the case that player did not send data in time. data
        #      will still be recieved and must be thrown out. send round number
        self.writer.write(json.dumps(game_state).encode() + b'\n')
        return json.loads(await self.reader.readline())


class Game():
    def __init__(self):
        self.x_bounds = (0, 400)
        self.y_bounds = (0, 400)
        self.state = {}
        self.players = []
        self.max_players = 2
    
    async def handle_new_connection(self, reader, writer):
        if len(self.players) >= self.max_players:
            raise Exception(f'Already {self.max_players} players in the game!')
        player_id = str(len(self.players))
        player = Player(player_id, reader, writer)
        self.players.append(player)
        self._update_state_new_player(player_id)
        # All players joined, start game
        if len(self.players) == self.max_players:
            await self.run()
    
    def _update_state_new_player(self, player_id):
        x, y = randint(*self.x_bounds), randint(*self.y_bounds)
        self.state.update({
            player_id: [x, y]
        })
    
    async def run(self):
        whos_turn = 0 # TODO async queue instead?
        # Game loop
        while True:
            print(self.state, type(self.state))
            next_player = self.players[whos_turn % self.max_players]
            self.state = await next_player.make_move(self.state)
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

class HTTPHandler():
    def __init__(self, game):
        self.game = game

    async def handle_game_state_request(self, request):
        game_state = self.game.state
        return web.json_response(game_state)

    async def handle_html_request(self, request):
        return web.FileResponse('./index.html')

# https://stackoverflow.com/questions/63055781/async-python-3-http-server-without-any-ready-made-web-frameworks-how
async def run_web_server(game):
    handler = HTTPHandler(game)
    app = web.Application()
    app.add_routes([
        web.get('/', handler.handle_html_request),
        web.get('/game_state', handler.handle_game_state_request),
        web.static('/static', './')
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    host = '127.0.0.1'
    port = 8080
    site = web.TCPSite(runner, host, port)
    print(f'Serving web server on {host}:{port}')
    await site.start()


async def main():
    game = Game()
    await asyncio.gather(run_tcp_server(game), run_web_server(game))


if __name__ == '__main__':
    asyncio.run(main())