# Sudeshna and Arkit wedding e-card

A cinematic digital invitation. The printed card is source material only. The website recreates the wording as HTML and uses the couple photographs as a photo film.

## How to open

Open `index.html` in a browser, or serve the folder:

```
npx --yes serve .
```

Tap **Open invitation**. Browsers block sound until that tap.

## Music

`WEDDING_MUSIC_URL` is set in `config.js` to `https://youtu.be/auQrLBUK_nk`.

The YouTube **video is not shown**. After the guest opens the card, that song plays in the background while the photographs animate. Use **Music on / Music off** to pause it.

YouTube is not a direct audio file, so it cannot be copied into the MP4 automatically. The downloadable video uses a separate legally usable soundtrack if `assets/wedding-music.mp3` is present. To put this exact song in the MP4, replace that file with a direct MP3 you have the right to use, then run:

```
python scripts/render_video.py
```

## Social preview

`assets/og.jpg` is a 1200 x 630 image of Sudeshna and Arkit with:

- Wedding invitation
- Sudeshna and Arkit
- 5 December 2026

After deploy, set the `og:image` and `twitter:image` tags in `index.html` to the full public URL of that file.

## Render helpers

```
python scripts/generate_og.py
python scripts/render_video.py
```
