/**
 * Generates thumbnail frames from a video URL using a hidden video element.
 * No crossOrigin attribute — avoids CORS failures on CDNs that don't send
 * Access-Control headers.
 */
export function generateThumbnails(
  src: string,
  duration: number,
  interval: number = 10,
  width: number = 160,
  height: number = 90,
): Promise<{ time: number; dataUrl: string }[]> {
  const results: { time: number; dataUrl: string }[] = [];
  const video = document.createElement('video');
  video.src = src;
  video.preload = 'auto';
  video.muted = true;
  video.setAttribute('playsinline', '');
  video.style.display = 'none';
  document.body.appendChild(video);

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) {
    video.remove();
    return Promise.resolve(results);
  }

  return new Promise((resolve) => {
    const cleanup = () => {
      video.removeEventListener('seeked', onSeeked);
      video.removeEventListener('loadedmetadata', onMeta);
      video.pause();
      video.src = '';
      video.remove();
      resolve(results);
    };

    const TIMEOUT = 30000;
    const timeout = setTimeout(cleanup, TIMEOUT);

    let pos = interval;

    const onMeta = () => {
      const d = video.duration || duration;
      if (d < 2 || pos >= d) {
        clearTimeout(timeout);
        cleanup();
        return;
      }
      video.currentTime = pos;
    };

    const onSeeked = () => {
      try {
        ctx.drawImage(video, 0, 0, width, height);
        results.push({
          time: video.currentTime,
          dataUrl: canvas.toDataURL('image/jpeg', 0.55),
        });
      } catch {
        // skip
      }

      pos += interval;
      const d = video.duration || duration;
      if (pos >= d) {
        clearTimeout(timeout);
        cleanup();
        return;
      }
      video.currentTime = pos;
    };

    video.addEventListener('loadedmetadata', onMeta, { once: true });
    video.addEventListener('seeked', onSeeked);
    video.load();
  });
}
