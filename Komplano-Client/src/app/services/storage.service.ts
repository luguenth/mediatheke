import { Injectable } from '@angular/core';
import { IVideo, IVideoLocalStorage } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class StorageService {

  constructor() { }

  private maxVideos = 100;

  setVideoPosition(video: IVideo, position: number): void {
    // Before adding a new video, check if we're at the limit.
    if (this.getStoredVideoCount() >= this.maxVideos) {
      this.removeOldestVideo();
    }

    const videoLocalStorage: IVideoLocalStorage = {
      id: video?.id,
      position: position,
      lastPlayedTimestamp: Date.now()
    };

    localStorage.setItem(`video_${video?.id}`, JSON.stringify(videoLocalStorage));
  }

  private getStoredVideoCount(): number {
    return Object.keys(localStorage).filter(key => key.startsWith('video_')).length;
  }

  private removeOldestVideo(): void {
    let oldestKey = null;
    let oldestTimestamp = Infinity;

    for (const [key, value] of Object.entries(localStorage)) {
      if (key.startsWith('video_')) {
        const videoData: IVideoLocalStorage = JSON.parse(value as string);
        if (videoData.lastPlayedTimestamp < oldestTimestamp) {
          oldestTimestamp = videoData.lastPlayedTimestamp;
          oldestKey = key;
        }
      }
    }

    if (oldestKey) {
      localStorage.removeItem(oldestKey);
    }
  }

  getVideoPosition(video: IVideo): number {
    const videoLocalStorage = localStorage.getItem(`video_${video?.id}`);
    if (videoLocalStorage) {
      const videoLocalStorageObject: IVideoLocalStorage = JSON.parse(videoLocalStorage);
      return videoLocalStorageObject.position;
    }
    return 0;
  }

  getVideoProgress(video: IVideo): number {
    const position = this.getVideoPosition(video);
    const duration = video?.duration || 0;
    return position / duration * 100;
  }

}
