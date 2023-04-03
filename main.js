// https://stackoverflow.com/questions/33843799/constantly-read-json-database

function $(a) {
  return document.getElementById(a)
}
function ajax(a, b, c) { // Url, Callback, just a placeholder
  c = new XMLHttpRequest;
  c.open('GET', a);
  c.onload = b;
  c.send()
}
function reloadData() {
  ajax('data.json', updateText)
};
function updateText() {
  var db = JSON.parse(this.response);
  console.log(db.x, db.y, db.z);
  $("x").innerHTML = db.x;
  $("y").innerHTML = db.y;
  $("z").innerHTML = db.z;
}
window.setInterval(reloadData, 100);//30 seconds 
