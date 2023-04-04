// https://stackoverflow.com/questions/33843799/constantly-read-json-database

let player1;
let player2;
const d = 50;

function setup() {
  createCanvas(400, 400);
  noStroke();
  player1 = {
    x: 0 + d,
    y: 0 + d,
    diameter: d
  };
  player2 = {
    x: 400 - d,
    y: 400 - d,
    diameter: d
  };
}

function playersColliding() {
  distance = Math.sqrt((player1.x - player2.x)**2 + (player1.y - player2.y)**2);
  if (distance < d) {
    return true;
  }
  return false;
}

function draw() {
  clear();
  loadJSON('p1Pos.json?' + Date.now(), updateBall);
  loadJSON('p2Pos.json?' + Date.now(), updateBall);
  fill(255, 0, 0);
  ellipse(player1.x, player1.y, player1.diameter, player1.diameter);
  if (playersColliding()) {
    fill(255, 0, 0); 
  } else {
    fill(0, 255, 0); 
  }
  ellipse(player2.x, player2.y, player2.diameter, player2.diameter);
}

function updateBall(data) {
  // update the ball position based on the data in the JSON file
  if (data.playerNumber == 1) {
    player1.x = data.x;
    player1.y = data.y;
  } else if (data.playerNumber == 2) {
    player2.x = data.x;
    player2.y = data.y;
  }
}
