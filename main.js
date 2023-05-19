const HOST = '127.0.0.1'; const PORT = 8080;
const FPS = 100; const msPerFrame = 1000 / FPS;

const HEIGHT = 400;
const WIDTH = 400;

let playerPositions;
const colorRGBs = [
  [0, 0, 255], // blue
  [0, 255, 0], // green
  [255, 0, 0], // red
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
