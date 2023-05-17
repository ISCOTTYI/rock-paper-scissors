const HOST = '127.0.0.1'; const PORT = 8080;
const FPS = 100; const msPerFrame = 1000 / FPS;

const HEIGHT = 400;
const WIDTH = 400;

let playerPositions;
const colorRGBs = [
  [255, 0, 0], // red
  [0, 255, 0], // green
  [0, 0, 255], // blue
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
    const data = await response.json();
    console.log(data);
    playerPositions = data;
    redraw(); // calls draw()
  } catch (error) {
    console.error(error);
  }
  setTimeout(pollPlayerPositions, msPerFrame);
}

function setup() {
  noLoop();
  createCanvas(HEIGHT, WIDTH, WEBGL);
  noStroke();
  pollPlayerPositions();
}

function drawAgent(agent, colorRGB = null) { //, symbol = null
  const ballDiameter = 50;
  if (colorRGB != null) {
    const [r, g, b] = colorRGB;
    fill(r, g, b);
  }
  let [agentType, x, y] = agent;
  texture(symbols[agentType]);
  // WEBGL places (0, 0) in the center of the canvas, correct that
  x -= WIDTH/2;
  y -= HEIGHT/2;
  circle(x, y, ballDiameter);
}

function draw() {
  clear();
  Object.keys(playerPositions).forEach((playerId, i) => {
    agents = playerPositions[playerId];
    agents.forEach(agent => { // problems if no players connected (only round)
      drawAgent(agent);
    });
  });
}
