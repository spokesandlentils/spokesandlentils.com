// Header video; see "Header video" in README.md. The photo is always there.
// The loop is loaded only for visitors who want motion and aren't
// on a slow/metered link, shown once it is really playing, and dropped if it
// hasn't started within 8 s (visible-tab time).
(() => {
  const video = document.querySelector('.hero-video');
  if (!video || !video.canPlayType('video/mp4')) return;

  const net = navigator.connection || {};  // Chromium only
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || net.saveData ||
      matchMedia('(prefers-reduced-data: reduce)').matches || /2g|3g/.test(net.effectiveType)) return;

  // data-srcset lists the same loop at several widths: take the smallest
  // that covers the header's width in screen pixels, else the largest.
  const pick = () => {
    const need = video.offsetWidth * (devicePixelRatio || 1);
    const sizes = video.dataset.srcset.split(',')
      .map((s) => s.trim().split(/\s+/))
      .map(([url, w]) => ({ url, w: parseInt(w, 10) }))
      .sort((a, b) => a.w - b.w);
    return (sizes.find((s) => s.w >= need - 1) || sizes[sizes.length - 1]).url;
  };

  let timer;
  const giveUp = () => {
    clearTimeout(timer);
    video.pause();
    video.removeAttribute('src');
    video.load();
    video.remove();
  };
  const wait = () => { timer = setTimeout(() => (document.hidden ? wait() : giveUp()), 8000); };

  const start = () => {
    wait();
    video.addEventListener('playing', () => {
      clearTimeout(timer);
      // Fade in only after a frame has been painted.
      if (video.requestVideoFrameCallback) video.requestVideoFrameCallback(() => video.classList.add('on'));
      else video.classList.add('on');
    }, { once: true });
    video.src = pick();
    video.play().catch(giveUp);
  };

  // Wait for the page (and so the photo) to load: the video never competes with it.
  if (document.readyState === 'complete') start();
  else addEventListener('load', start, { once: true });
})();
