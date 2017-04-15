function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function addCoin() {
  var audio = new Audio('/static/audio/coin.mp3');
  audio.play();
  $(".coin-container").append(
    '<img src="/static/images/aureus.png" alt="Roman coin" width="60" height="60", style="margin: 5px">'
  );
}

(function myLoop(i) {
  sleep(180).then(() => {
    addCoin()
    if (--i) {
      myLoop(i)
    } else {
      sleep(1000).then(() => {
        var audio = new Audio('/static/audio/level-up.mp3');
        audio.play();
        xpChart()
        }
      )
    }

  });
})(score)
