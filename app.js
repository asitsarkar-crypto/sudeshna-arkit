const config = window.WEDDING_CONFIG;
const MUSIC_KEY = "sudeshna-arkit-music";
const gate = document.querySelector("#gate");
const enter = document.querySelector("#enter");
const story = document.querySelector("#story");
const shots = [...document.querySelectorAll(".shot")];
const musicDock = document.querySelector("#music-dock");
const musicToggle = document.querySelector("#music-toggle");
const downloadPdf = document.querySelector("#download-pdf");
const downloadMp4 = document.querySelector("#download-mp4");
const downloadStatus = document.querySelector("#download-status");
const song = document.querySelector("#wedding-song") || new Audio(config.WEDDING_SONG_FILE || "assets/wedding-song.mp3");

song.loop = true;
song.preload = "auto";
song.volume = 0.9;

let musicOn = window.localStorage.getItem(MUSIC_KEY) !== "off";
let shotTimer = 0;
let shotIndex = 0;

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
  musicToggle.setAttribute("aria-pressed", String(musicOn));
}

function rememberMusic() {
  window.localStorage.setItem(MUSIC_KEY, musicOn ? "on" : "off");
}

async function playSong() {
  try {
    await song.play();
    musicOn = true;
  } catch (error) {
    musicOn = false;
  }
  rememberMusic();
  setMusicLabel();
}

function toggleSong() {
  if (musicOn) {
    song.pause();
    musicOn = false;
  } else {
    song.play().then(() => {
      musicOn = true;
      rememberMusic();
      setMusicLabel();
    }).catch(() => {
      musicOn = false;
      rememberMusic();
      setMusicLabel();
    });
    return;
  }
  rememberMusic();
  setMusicLabel();
}

function openInvitation() {
  story.hidden = false;
  if (musicDock) musicDock.hidden = false;
  gate.classList.add("is-away");
  if (musicOn) {
    playSong();
  } else {
    setMusicLabel();
  }
  playFilm();
  window.setTimeout(() => {
    gate.hidden = true;
  }, 900);
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
setMusicLabel();
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
