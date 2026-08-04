let time = 30;
const timer = document.getElementById("timer");

const t = setInterval(() => {
  time--;
  timer.innerText = "⏱ Time: " + time;
  if (time <= 0) {
    clearInterval(t);
    playTimeout();
    alert("Time up!");
    location.reload();
  }
}, 1000);
