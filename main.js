let player1 = {
  x: 0,
  y: 0
};
let player2 = {
  x: 0,
  y: 0
}
const d = 50;

// async function requestPositions() {
//   fetch('http://localhost:8000/state')
//     .then(response => response.json())
//     .then(data => {
//       console.log(data);
//       player1.x = data.x1;
//       player1.y = data.y1;
//       player2.x = data.x2;
//       player2.y = data.y2;
//     });
// }

async function requestPlayerPositions() {
  try {
    let response = await fetch('http://localhost:8000/state');
    return response.json();
  } catch (error) {
    console.error(error);
  }
}

function setup() {
  createCanvas(400, 400);
  noStroke();
}

function playersColliding(positions) {
  deltaX = positions["x1"] - positions["x2"];
  deltaY = positions["y1"] - positions["y2"];
  distance = Math.sqrt((deltaX)**2 + (deltaY)**2);
  if (distance < d) {
    return true;
  }
  return false;
}



// async function draw() {
//   // Do not fetch here, but in a seperate function that writes to variable.
//   // only fetch every 10 ms or so...
//   let positions = await requestPlayerPositions();
//   console.log(positions);
//   clear();
//   fill(255, 0, 0);
//   ellipse(positions["x1"], positions["y1"], d, d);
//   if (playersColliding(positions)) {
//     fill(255, 0, 0); 
//   } else {
//     fill(0, 255, 0); 
//   }
//   ellipse(positions["x2"], positions["y2"], d, d);
// }

// fetch('http://localhost:8000/state')
//   .then(response => response.json())
//   .then(data => console.log(data));

