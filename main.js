// https://stackoverflow.com/questions/33843799/constantly-read-json-database

let player1 = {
  x: 0,
  y: 0
};
let player2 = {
  x: 0,
  y: 0
}
const d = 50;

function make_fetch() {
  fetch('http://localhost:8000/state')
    .then(response => response.json())
    .then(data => {
      console.log(data);
      player1.x = data.x1;
      player1.y = data.y1;
      player2.x = data.x2;
      player2.y = data.y2;
    });
}

function setup() {
  createCanvas(400, 400);
  noStroke();
  make_fetch();
}

function playersColliding() {
  distance = Math.sqrt((player1.x - player2.x)**2 + (player1.y - player2.y)**2);
  if (distance < d) {
    return true;
  }
  return false;
}

function draw() {
  make_fetch();
  clear();
  fill(255, 0, 0);
  ellipse(player1.x, player1.y, d, d);
  if (playersColliding()) {
    fill(255, 0, 0); 
  } else {
    fill(0, 255, 0); 
  }
  ellipse(player2.x, player2.y, d, d);
}

// fetch('http://localhost:8000/state')
//   .then(response => response.json())
//   .then(data => console.log(data));

