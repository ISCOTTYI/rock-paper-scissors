const HOST = '127.0.0.1'; const PORT = 8080;
const FPS = 100; const msPerFrame = 1000 / FPS;

const HEIGHT = 400;
const WIDTH = 400;

let playerPositions;
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
    "0": loadImage(`/static/rock_scaled.png`),
    "1": loadImage(`/static/paper_scaled.png`),
    "2": loadImage(`/static/scissors_scaled.png`)
  };
}

async function pollPlayerPositions() {
  try {
    const response = await fetch("/game_state");
    let data = await response.json();
    delete data.round;
    console.log(data);
    playerPositions = data;
    redraw(); // calls draw()
    game_stats_handler();
  } catch (error) {
    console.error(error);
  }
  setTimeout(pollPlayerPositions, msPerFrame);
}

function game_stats_handler() {
  Object.keys(playerPositions).forEach((playerId, i) => {
    const counts = playerPositions[playerId].reduce((acc, [value]) => {
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    }, {});
    let playerCard = `<div id=card-${playerId} class="card ${cardClasses[i]} text-white mb-2">
        <div class="card-header"><strong>Player ${playerId}</strong></div>
        <ul class="list-group list-group-flush text-primary">
          <li id="card-${playerId}-rocks" class="list-group-item comic-font">REMAINING 🪨 : ${counts["0"]}</li>
          <li id="card-${playerId}-papers" class="list-group-item comic-font">REMAINING 📜 : ${counts["1"]}</li>
          <li id="card-${playerId}-scissors" class="list-group-item comic-font">REMAINING ✂️ : ${counts["2"]}</li>
        </ul>
      </div>`;
    let cardElement = document.getElementById(`card-${playerId}`);
    if (!cardElement) {
      document.getElementById("game-stats-container").innerHTML += playerCard;
    } else {
      document.getElementById(`card-${playerId}-rocks`).innerHTML = `REMAINING 🪨 : ${counts["0"]}`;
      document.getElementById(`card-${playerId}-papers`).innerHTML = `REMAINING 📜 : ${counts["1"]}`;
      document.getElementById(`card-${playerId}-scissors`).innerHTML = `REMAINING ✂️ : ${counts["2"]}`;
    }
  })
}

function setup() {
  noLoop();
  let canvas = createCanvas(HEIGHT, WIDTH, WEBGL);
  canvas.parent('simulation');
  noStroke();
  pollPlayerPositions();
}

function drawAgent(agent, colorRGB = null) { //, symbol = null
  let [agentType, x, y] = agent;
  const ballDiameter = 20;
  // WEBGL places (0, 0) in the center of the canvas, correct that
  x -= WIDTH/2;
  y -= HEIGHT/2;
  if (colorRGB != null) {
    const [r, g, b] = colorRGB;
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
