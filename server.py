import asyncio
import json
import logging
import math
import argparse
from aiohttp import web
from random import randint
from itertools import combinations

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_const', const=True)
if parser.parse_args().debug:
    logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)
logger.addHandler(handler)
    
class Agent():
    count = 0
    def __init__(self, x, y, r, owner, kind=None):
        self.id = Agent.count
        Agent.count += 1
        if kind is None:
            kind = randint(0, 2)
        assert kind in (0, 1, 2)
        self.kind = kind
        self.x = x
        self.y = y
        self.r = r
        self.owner = owner

    def json_serializable(self):
        return [self.id, str(self.kind), self.x, self.y]
    
    def move_agent(self, x, y):
        self.x = x
        self.y = y
    
    def vs(self, opponent_agent):
        '''
        0 - tie or no collision, 1 - self won, -1 - opponent won
        '''
        if not self.colliding_with(opponent_agent):
            return 0
        if self.owner.id == opponent_agent.owner.id:
            pass # different outcome if same player
        # https://codereview.stackexchange.com/questions/240494/rock-paper-scissors-without-arrays-and-if-statements-how-to-reduce
        outcome = (self.kind - opponent_agent.kind + 4) % 3 - 1
        return outcome
    
    def colliding_with(self, opponent_agent):
        dx = abs(self.x - opponent_agent.x)
        dy = abs(self.y - opponent_agent.y)
        d = math.sqrt(dx**2 + dy**2)
        if d < self.r + opponent_agent.r:
            return True
        return False


class Player():
    # count = 0
    def __init__(self, id, reader, writer):
        # self.id = Player.count
        # Player.count += 1
        self.id = id
        self.reader = reader
        self.writer = writer
        self._agents = {}
    
    @property
    def agents(self):
        return list(self._agents.values())

    def agent(self, id):
        if id in self._agents:
            return self._agents[id]
        raise Exception(f"Agent {id} does not belong to player {self.id}!")
    
    def json_serializable(self):
        return self.agents

    def add_agent(self, agent):
        self._agents.update({agent.id: agent})
    
    def remove_agent(self, agent):
        del self._agents[agent.id]

    def move_agent_owner_to(self, player, agent):
        assert agent.id in self._agents
        # Don't do anything if owner is already 'player'
        if self.id == player.id:
            return
        player.add_agent(agent)
        self.remove_agent(agent)
        agent.owner = player

    async def send_move_request(self, game_state):
        '''
        Send a move request to the player. The request consists of sending the
        game_state and waiting for moves in response. The moves are returned.
        '''
        round = game_state["round"]
        jsoned_state = json.dumps(
            game_state, default=lambda o: o.json_serializable())
        self.writer.write(jsoned_state.encode() + b'\n')
        response = json.loads(await self.reader.readline())
        # Make sure response is not a delayed response from a skipped round
        while response["round"] != round:
            logger.debug(
                f'Recieved delayed response from round {response["round"]}')
            response = json.loads(await self.reader.readline())
        return response["moves"]
    
    async def make_move(self, game_state):
        # TODO catch error if player disconnects
        MAX_TIMEOUT = 0.1 # 100 ms
        try:
            moves = await asyncio.wait_for(
                self.send_move_request(game_state), timeout=MAX_TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            logger.warning(f'Player {self.id} timed out...')
            moves = []
        return moves
    

class Game():
    def __init__(self):
        self.x_bounds = (0, 400)
        self.y_bounds = (0, 400)
        self.radius = 10
        self.players = []
        # self.state = {"round": 0}
        self.round = 0
        self.max_players = 2
        self.agents_per_player = 15
        self.max_v = 1
    
    @property
    def game_state(self):
        state = {"round": self.round}
        state.update(self.json_serializable())
        return state

    @property
    def agents(self):
        return sum([player.agents for player in self.players], [])
    
    def json_serializable(self):
        return {player.id: player for player in self.players}

    def __str__(self):
        return json.dumps(
            self.game_state, default=lambda o: o.json_serializable())
    
    async def handle_new_connection(self, reader, writer):
        if len(self.players) >= self.max_players:
            raise Exception(f'Already {self.max_players} players in the game!')
        player_id = str(len(self.players))
        player = Player(player_id, reader, writer)
        addr = (await player.reader.readline()).decode()[:-1]
        player.writer.write(player_id.encode() + b'\n')
        logger.info(f'Player {player_id} with socket address {addr} joined!')
        self.add_player(player, self.agents_per_player)
        logger.info(f'Waiting for {self.max_players - len(self.players)} more player to join...')
        # All players joined, start game
        if len(self.players) == self.max_players:
            logger.info('All players joined, starting game!')
            logger.debug(str(self))
            await asyncio.sleep(3)
            await self.run()
    
    def add_player(self, player, number_of_agents):
        self.players.append(player)
        for _ in range(number_of_agents):
            x, y = randint(*self.x_bounds), randint(*self.y_bounds)
            player.add_agent(Agent(x, y, self.radius, player))
    
    def handle_collisions(self):
        for agent, opponent in combinations(self.agents, 2):
            outcome = agent.vs(opponent)
            if outcome == 0: # tie or no collision
                continue
            elif outcome == 1: # agent won
                opponent.kind = agent.kind
                opponent.owner.move_agent_owner_to(agent.owner, opponent)
            else: # opponent won
                agent.kind = opponent.kind
                agent.owner.move_agent_owner_to(opponent.owner, agent)
    
    def parse_player_moves(self, player, moves):
        '''
        moves is list of [id, v, phi] pairs in order of player agents
        '''
        for move in moves:
            id, v, phi = move
            try:
                agent = player.agent(int(id))
            except Exception:
                logger.warning(f'Player {player.id} sent move for unowned agent {id}')
                continue
            assert 0 <= v <= self.max_v
            assert 0 <= phi <= 2*math.pi
            x_dir = math.cos(phi)
            y_dir = math.sin(phi)
            agent.move_agent(
                (agent.x + v * x_dir) % self.x_bounds[1],
                (agent.y + v * y_dir) % self.y_bounds[1],
            )
    
    def game_over(self):
        # if one player has no more agents, game is over
        for player in self.players:
            if not player.agents:
                return True
        return False
            
    async def run(self):
        whos_turn = 0 # TODO async queue instead?
        # Game loop
        while True:
            if self.game_over():
                logger.info("Game is over!")
                break
            logger.debug(str(self))
            next_player = self.players[whos_turn % self.max_players]
            moves = await next_player.make_move(self.game_state)
            self.parse_player_moves(next_player, moves)
            self.handle_collisions()
            whos_turn += 1
            self.round += 1

class HTTPHandler():
    def __init__(self, game):
        self.game = game

    async def handle_game_state_request(self, request):
        game_state = self.game.game_state
        my_dumps = lambda d: json.dumps(d, default=lambda o: o.json_serializable())
        return web.json_response(game_state, dumps=my_dumps)

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
        web.static('/static', './static')
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