const config = window.WEDDING_CONFIG;
const gate = document.querySelector("#gate");
const enter = document.querySelector("#enter");
const story = document.querySelector("#story");
const shots = [...document.querySelectorAll(".shot")];
const musicDock = document.querySelector("#music-dock");
const musicToggle = document.querySelector("#music-toggle");
const downloadPdf = document.querySelector("#download-pdf");
const downloadMp4 = document.querySelector("#download-mp4");
const downloadStatus = document.querySelector("#download-status");

let player = null;
let musicOn = false;
let wantMusic = false;
let shotTimer = 0;
let shotIndex = 0;
let playAttempts = 0;

function splitLetters() {
  document.querySelectorAll("[data-letters]").forEach((node) => {
    const text = node.dataset.letters;
    node.textContent = "";
    [...text].forEach((char, index) => {
      const span = document.createElement("span");
      span.className = "letter";
      span.style.animationDelay = `${0.55 + index * 0.07}s`;
      span.textContent = char;
      node.append(span);
    });
  });
}

function showShot(index) {
  shots.forEach((shot, i) => shot.classList.toggle("is-on", i === index));
}

function playFilm() {
  window.clearTimeout(shotTimer);
  showShot(shotIndex);
  const duration = Number(shots[shotIndex].dataset.duration) || 7000;
  shotTimer = window.setTimeout(() => {
    shotIndex = (shotIndex + 1) % shots.length;
    playFilm();
  }, duration);
}

function setMusicLabel() {
  musicToggle.textContent = musicOn ? "Music on" : "Music off";
}

function startPlayer() {
  if (!player || typeof player.playVideo !== "function") return false;
  try {
    player.unMute();
    player.setVolume(90);
    player.playVideo();
    return true;
  } catch (error) {
    return false;
  }
}

function playSong() {
  wantMusic = true;
  if (!startPlayer()) return;
  window.setTimeout(() => {
    const state = player && player.getPlayerState ? player.getPlayerState() : -1;
    if (state === 1) {
      musicOn = true;
      setMusicLabel();
      return;
    }
    if (playAttempts < 6) {
      playAttempts += 1;
      startPlayer();
    }
  }, 500);
}

function toggleSong() {
  if (!player) return;
  if (musicOn) {
    player.pauseVideo();
    wantMusic = false;
    musicOn = false;
  } else {
    playAttempts = 0;
    playSong();
  }
  setMusicLabel();
}

window.onYouTubeIframeAPIReady = function onYouTubeIframeAPIReady() {
  player = new YT.Player("yt-audio", {
    videoId: config.YOUTUBE_ID,
    width: 220,
    height: 124,
    host: "https://www.youtube-nocookie.com",
    playerVars: {
      autoplay: 0,
      controls: 0,
      disablekb: 1,
      fs: 0,
      modestbranding: 1,
      playsinline: 1,
      rel: 0,
      loop: 1,
      playlist: config.YOUTUBE_ID,
    },
    events: {
      onReady() {
        if (wantMusic) playSong();
      },
      onStateChange(event) {
        if (event.data === YT.PlayerState.PLAYING) {
          musicOn = true;
          setMusicLabel();
        }
        if (event.data === YT.PlayerState.PAUSED && !wantMusic) {
          musicOn = false;
          setMusicLabel();
        }
        if (event.data === YT.PlayerState.ENDED) {
          player.playVideo();
        }
      },
      onError() {
        musicOn = false;
        setMusicLabel();
        musicToggle.textContent = "Music unavailable";
      },
    },
  });
};

function openInvitation() {
  story.hidden = false;
  musicDock.hidden = false;
  gate.classList.add("is-away");
  playAttempts = 0;
  playSong();
  playFilm();
  window.setTimeout(() => {
    gate.hidden = true;
    playSong();
  }, 400);
}

async function downloadFile(url, filename, preparing, ready, missing) {
  downloadStatus.textContent = preparing;
  try {
    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) throw new Error("missing");
    const blob = await response.blob();
    if (blob.size < 2000) throw new Error("empty");
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(objectUrl);
    downloadStatus.textContent = ready;
  } catch (error) {
    downloadStatus.textContent = missing;
  }
}

splitLetters();
enter.addEventListener("click", openInvitation);
musicToggle.addEventListener("click", toggleSong);
downloadPdf.addEventListener("click", () => {
  downloadFile(
    config.PDF_URL,
    "sudeshna-arkit-wedding-invitation.pdf",
    "Preparing the invitation PDF...",
    "Your invitation PDF is ready.",
    "The PDF is still being prepared. Please try again in a moment.",
  );
});
downloadMp4.addEventListener("click", () => {
  downloadFile(
    config.MP4_URL,
    "sudeshna-arkit-wedding-ecard.mp4",
    "Preparing the wedding film...",
    "Your wedding MP4 is ready.",
    "The MP4 is still being prepared. Please try again in a moment.",
  );
});
