# Rock-Paper-Scissors World Cup Game
This is a rock-paper-scissors multiplayer game. The players move their agents (rocks,
papers and scissors) on a 2D playing field. A classical rock-paper-scissors fight
takes place upon collision of two agents.

![Image](screenshot.png)

## Technical Details
The players communicate with the game via TCP (game server). The game is visualized
on a website. The web server and the game server run asynchronously and are both
controlled by `server.py`. The game logic is fully handled by the server side.

## TODO
- [x] `Player.make_move()` error catching
- [ ] C++ client
  - [x] Basic communication
  - [x] Parse JSON
  - [ ] Needs a `readline()` from TCP stream (buffering) (DONE?)
- [x] Parse player response, should not modify whole game state
- [x] Player response rules
- [x] BUG: Website does not update when players join
- [ ] Fix the framerate of the game, i.e. make sure that every move takes the same time regardless of player response times.
- [x] Make sure that the client is automatically assigned its ID
- [x] Color Code Player Agents
- [ ] What if only one kind remains?
- [ ] Change game state format such that it is easier to count rocks, papers, scissors
