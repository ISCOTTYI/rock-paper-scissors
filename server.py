import asyncio
import json
import logging
from aiohttp import web
from random import randint
import numpy as np
from itertools import combinations

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Player():
    def __init__(self, id, reader, writer):
        self.id = id
        self.reader = reader
        self.writer = writer
    
    async def _make_move(self, game_state):
        round = game_state["round"]
        self.writer.write(json.dumps(game_state).encode() + b'\n')
        response = json.loads(await self.reader.readline())
        print(response)
        # Make sure response is not a delayed response from a skipped round
        while response["round"] != round:
            logger.debug(f'Recieved delayed response from round {response["round"]}')
            response = json.loads(await self.reader.readline())
        return response["moves"]
    
    async def make_move(self, game_state):
        # TODO catch error if player disconnects, takes too long or other shit
        # TODO deal with the case that player did not send data in time. data
        #      will still be recieved and must be thrown out. send round number
        MAX_TIMEOUT = 0.01 # 10 ms
        try:
            moves = await asyncio.wait_for(
                self._make_move(game_state), timeout=MAX_TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            logger.warning(f'Player {self.id} timed out...')
            moves = []
        return moves
    

class Game():
    def __init__(self):
        self.x_bounds = (0, 400)
        self.y_bounds = (0, 400)
        self.radius = 25
        self.players = []
        self.state = {"round": 0}
        self.max_players = 2

    @property
    def agents(self):
        return [
            (player.id, i, agent)
            for player in self.players
            for i, agent in enumerate(self.state[player.id])
        ]
    
    async def handle_new_connection(self, reader, writer):
        if len(self.players) >= self.max_players:
            raise Exception(f'Already {self.max_players} players in the game!')
        player_id = str(len(self.players))
        player = Player(player_id, reader, writer)
        addr = (await player.reader.readline()).decode()[:-1]
        logger.info(f'Player {player_id} with socket address {addr} joined!')
        self.add_player(player)
        # All players joined, start game
        if len(self.players) == self.max_players:
            logger.info('All players joined, starting game!')
            logger.debug(self.state)
            import time
            time.sleep(2)
            await self.run()
    
    def add_player(self, player):
        self.players.append(player)
        x, y = randint(*self.x_bounds), randint(*self.y_bounds)
        agent_type = ["0", "1", "2"][randint(0, 2)]
        agent = [agent_type, x, y]
        self.state.update({player.id: [agent]})

    def rps_fight(self, player_agent, opponent_agent, same_player=False):
        '''
        For a given player_agent and opponent agent in format (agent_type, x, y),
        return the player and opponent agent after a rock-paper-scissors fight.
        '''
        player_agent_type = player_agent[0]
        opponent_agent_type = opponent_agent[0]
        if same_player:
            pass
        # https://codereview.stackexchange.com/questions/240494/rock-paper-scissors-without-arrays-and-if-statements-how-to-reduce
        # Player and opponent are one out of rock (0), paper(1), scissors(2)
        # Returns 1 if player won, -1 if player lost, 0 for a tie
        winner = (int(player_agent_type) - int(opponent_agent_type) + 4) % 3 - 1
        if winner == 1:
            opponent_agent[0] = player_agent_type
        elif winner == -1:
            player_agent[0] = opponent_agent_type
        return player_agent, opponent_agent
    
    def are_colliding(self, player_agent, opponent_agent):
        player_vec = np.array(player_agent[1:])
        opponent_vec = np.array(opponent_agent[1:])
        distance_vec = np.abs(player_vec - opponent_vec)
        if np.all(distance_vec < self.radius):
            return True
        return False
    
    def handle_collisions(self):
        for p, o in combinations(self.agents, 2):
            p_id, p_i, p_agent = p
            o_id, o_i, o_agent = o
            if self.are_colliding(p_agent, o_agent):
                p_agent, o_agent = self.rps_fight(p_agent, o_agent)
                self.state[p_id][p_i] = p_agent
                self.state[o_id][o_i] = o_agent
    
    def player_moves_to_state(self, player_id, moves):
        '''
        moves is list of [v, phi] pairs in order of player agents
        '''
        for i, move in enumerate(moves):
            v, phi = move
            assert 0 <= v <= 0.1
            assert 0 <= phi <= 2 * np.pi
            x_orientation, y_orientation = np.cos(phi), np.sin(phi)
            x = self.state[str(player_id)][i][1]
            y = self.state[str(player_id)][i][2]
            self.state[str(player_id)][i][1] = (x + v * x_orientation) % self.x_bounds[1]
            self.state[str(player_id)][i][2] = (y + v * y_orientation) % self.y_bounds[1]
    
    def game_over(self):
        # if one player has no more agents, game is over
        for player in self.players:
            if not self.state[player.id]:
                return True
        return False
            
    async def run(self):
        whos_turn = 0 # TODO async queue instead?
        # Game loop
        while True:
            if self.game_over:
                break
            logger.debug(self.state)
            next_player = self.players[whos_turn % self.max_players]
            moves = await next_player.make_move(self.state)
            self.player_moves_to_state(next_player.id, moves)
            self.handle_collisions()
            whos_turn += 1
            self.state["round"] += 1

class HTTPHandler():
    def __init__(self, game):
        self.game = game

    async def handle_game_state_request(self, request):
        game_state = self.game.state
        return web.json_response(game_state)

    async def handle_html_request(self, request):
        return web.FileResponse('./index.html')


async def run_tcp_server(game):
    server = await asyncio.start_server(
        game.handle_new_connection, '127.0.0.1', 9999)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving game server on {addrs}')

    async with server:
        await server.serve_forever()


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
    print(f'Serving web server on {(host, port)}')
    await site.start()


async def main():
    game = Game()
    await asyncio.gather(run_tcp_server(game), run_web_server(game))


if __name__ == '__main__':
    asyncio.run(main())