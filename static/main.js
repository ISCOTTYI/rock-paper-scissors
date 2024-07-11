const HOST = '127.0.0.1'; const PORT = 8080;
const FPS = 100; const msPerFrame = 1000 / FPS;

const HEIGHT = 400;
const WIDTH = 400;

let playerPositions;
let nicknames;
let numberOfPlayers = 0;

const colorRGBs = [
  [0, 0, 255], // blue
  [255, 0, 0], // red
  [0, 255, 0], // green
];
const cardClasses = [
  "bg-primary", // blue
  "bg-danger", //red
  "bg-success", // green
];

let symbols;
function preload() {
  symbols = {
    "0": loadImage(`/static/rock.png`),
    "1": loadImage(`/static/paper.png`),
    "2": loadImage(`/static/scissors.png`)
  };
}

async function pollPlayerPositions() {
  try {
    const response = await fetch("/game_state");
    let data = await response.json();
    console.log(data);
    if (data.round == 0) {
      await setPlayerNicknames();
    }
    delete data.round;
    playerPositions = data;
    redraw(); // calls draw()
    game_stats_handler();
  } catch (error) {
    console.error(error);
  }
  setTimeout(pollPlayerPositions, msPerFrame);
}

async function setPlayerNicknames() {
  try{
    const response = await fetch("/nicknames");
    let stringNicknames = await response.text();
    nicknames = stringNicknames.split('~');
    console.log(nicknames);
  } catch (error) {
    console.error(error);
  }
}

function game_stats_handler() {
  Object.keys(playerPositions).forEach((playerId, i) => {
    const counts = playerPositions[playerId].reduce((acc, curr) => {
      const key = curr[1];
      if (!acc[key]) {
        acc[key] = 0;
      }
      acc[key]++;
      return acc;
    }, {});
    const nickname = nicknames[playerId];
    let playerCard = `<div id=card-${playerId} class="card ${cardClasses[i]} text-white mb-2">
        <div class="card-header"><strong>Player ${playerId}: ${nickname}</strong></div>
        <ul class="list-group list-group-flush text-primary">
          <li class="list-group-item comic-font">REMAINING <span class="emoji-font">🪨</span> : <span id="card-${playerId}-rocks">${counts["0"] == undefined ? 0 : counts["0"]}</span></li>
          <li class="list-group-item comic-font">REMAINING <span class="emoji-font">📜</span> : <span id="card-${playerId}-papers">${counts["1"] == undefined ? 0 : counts["1"]}</span></li>
          <li class="list-group-item comic-font">REMAINING <span class="emoji-font">✂️</span> : <span id="card-${playerId}-scissors">${counts["2"] == undefined ? 0 : counts["2"]}</span></li>
        </ul>
      </div>`;
    let cardElement = document.getElementById(`card-${playerId}`);
    if (!cardElement) {
      document.getElementById("game-stats-container").innerHTML += playerCard;
    } else {
      document.getElementById(`card-${playerId}-rocks`).innerHTML = `${counts["0"] == undefined ? 0 : counts["0"]}`;
      document.getElementById(`card-${playerId}-papers`).innerHTML = `${counts["1"] == undefined ? 0 : counts["1"]}`;
      document.getElementById(`card-${playerId}-scissors`).innerHTML = `${counts["2"] == undefined ? 0 : counts["2"]}`;
    }
  })
}

function setup() {
  noLoop();
  let canvas = createCanvas(HEIGHT, WIDTH, WEBGL);
  canvas.parent('simulation');
  noStroke();
  setPlayerNicknames();
  pollPlayerPositions();
}

function drawAgent(agent, colorRGB = null) { //, symbol = null
  let [id, agentType, x, y] = agent;
  const ballDiameter = 20;
  // WEBGL places (0, 0) in the center of the canvas, correct that
  x -= WIDTH/2;
  y -= HEIGHT/2;
  if (colorRGB != null) {
    const [r, g, b] = colorRGB;
    strokeWeight(2);
    stroke(r, g, b);
  }
  texture(symbols[agentType]);
  circle(x, y, ballDiameter);
}

function draw() {
  clear();
  Object.keys(playerPositions).forEach((playerId, i) => {
    agents = playerPositions[playerId];
    agents.forEach(agent => {
      drawAgent(agent, colorRGB=colorRGBs[i]);
    });
  });
}
