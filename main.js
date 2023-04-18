const gameStateUrl = 'http://localhost:8080/game_state'

// Ball diameter
const d = 50;

let playerPositions;

// async function requestPlayerPositions() {
//   try {
//     let response = await fetch(gameStateUrl);
//     let gameState = response.json();
//     console.log(gameState);
//     setTimeout(requestPlayerPositions, 1000);
//     return gameState;
//   } catch (error) {
//     console.error(error);
//   }
// }
async function pollPlayerPositions() {
  try {
    const response = await fetch(gameStateUrl);
    const data = await response.json();
    console.log(data);
    playerPositions = data;
  } catch (error) {
    console.error(error);
  }
  setTimeout(pollPlayerPositions, 10);
}

function setup() {
  createCanvas(400, 400);
  noStroke();
  pollPlayerPositions();
}

function playersColliding() {
  deltaX = playerPositions['0'][0] - playerPositions['1'][0];
  deltaY = playerPositions['0'][1] - playerPositions['1'][1];
  distance = Math.sqrt((deltaX)**2 + (deltaY)**2);
  if (distance < d) {
    return true;
  }
  return false;
}

function draw() {
  // Do not fetch here, but in a seperate function that writes to variable.
  // only fetch every 10 ms or so...
  clear();
  fill(255, 0, 0);
  ellipse(playerPositions['0'][0], playerPositions['0'][1], d, d);
  if (playersColliding()) {
    fill(255, 0, 0); 
  } else {
    fill(0, 255, 0); 
  }
  ellipse(playerPositions['1'][0], playerPositions['1'][1], d, d);
}
