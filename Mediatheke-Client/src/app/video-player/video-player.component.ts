import { Component, Input, ElementRef, SimpleChanges, ViewChild, OnInit, OnChanges, AfterViewInit, HostListener, EventEmitter, Output } from '@angular/core';
import { IVideo } from '../interfaces';
import { StorageService } from '../services/storage.service';

export enum VideoQuality {
  SMALL = "SD",
  BASE = "MD",
  HD = "HD"
}

export enum AudioTrack {
  REGULAR = "DE",
  AD = "AD",
  UT = "UT",
  OV = "OV",
  OV_UT = "OV+UT"
}

interface TrackInfo {
  track: AudioTrack;
  label: string;
  icon: string;
  hasUrls: (v: IVideo) => boolean;
  getUrl: (v: IVideo, quality: VideoQuality) => string;
}

const TRACKS: TrackInfo[] = [
  {
    track: AudioTrack.REGULAR,
    label: 'DE',
    icon: '',
    hasUrls: (v) => !!v.url_video,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL: return v.url_video_low;
        case VideoQuality.HD: return v.url_video_hd;
        default: return v.url_video;
      }
    }
  },
  {
    track: AudioTrack.AD,
    label: 'AD',
    icon: 'ear-fill',
    hasUrls: (v) => !!v.url_video_descriptive_audio,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL: return v.url_video_low_descriptive_audio;
        case VideoQuality.HD: return v.url_video_hd_descriptive_audio;
        default: return v.url_video_descriptive_audio;
      }
    }
  },
  {
    track: AudioTrack.UT,
    label: 'UT',
    icon: 'badge-cc-fill',
    hasUrls: (v) => !!v.url_video_ut,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL: return v.url_video_low_ut;
        case VideoQuality.HD: return v.url_video_hd_ut;
        default: return v.url_video_ut;
      }
    }
  },
  {
    track: AudioTrack.OV,
    label: 'OV',
    icon: 'globe2',
    hasUrls: (v) => !!v.url_video_ov,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL: return v.url_video_low_ov;
        case VideoQuality.HD: return v.url_video_hd_ov;
        default: return v.url_video_ov;
      }
    }
  },
  {
    track: AudioTrack.OV_UT,
    label: 'OV+UT',
    icon: 'globe2',
    hasUrls: (v) => !!v.url_video_ov_ut,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL: return v.url_video_low_ov_ut;
        case VideoQuality.HD: return v.url_video_hd_ov_ut;
        default: return v.url_video_ov_ut;
      }
    }
  },
];

@Component({
  selector: 'app-video-player',
  templateUrl: './video-player.component.html',
  styleUrls: ['./video-player.component.scss']
})
export class VideoPlayerComponent implements OnInit, OnChanges, AfterViewInit {
  @Input() video: IVideo | undefined;
  @Input() urlTime: number = 0;
  @Output() currentTime = new EventEmitter<number>();
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('wrapperElement') wrapperElement!: ElementRef;

  QualityEnum = VideoQuality;
  AudioTrackEnum = AudioTrack;
  availableQualities: VideoQuality[] = [];
  availableTracks: AudioTrack[] = [];
  curr_quality = VideoQuality.BASE;
  curr_track = AudioTrack.REGULAR;
  viewInitialized = false;
  showSlider = false;

  constructor(
    private storageService: StorageService
  ) { }

  ngOnInit(): void {
    this.setVideoSource(this.getLastKnownTime());
    this.updateAvailableOptions();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.viewInitialized && changes.video && changes.video.currentValue) {
      this.video = changes.video.currentValue;
      this.updateAvailableOptions();
      this.setVideoSource(this.getLastKnownTime());
    }
  }

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    this.setVideoSource(this.urlTime !== 0 ? this.urlTime : this.getLastKnownTime());
  }

  updateAvailableOptions(): void {
    if (!this.video) return;
    this.availableQualities = [];
    if (this.video.url_video) this.availableQualities.push(VideoQuality.BASE);
    if (this.video.url_video_low) this.availableQualities.push(VideoQuality.SMALL);
    if (this.video.url_video_hd) this.availableQualities.push(VideoQuality.HD);

    this.availableTracks = TRACKS
      .filter(t => t.hasUrls(this.video!))
      .map(t => t.track);

    // Reset track if current one is no longer available
    if (!this.availableTracks.includes(this.curr_track)) {
      this.curr_track = AudioTrack.REGULAR;
    }
  }

  getTrackInfo(track: AudioTrack): TrackInfo | undefined {
    return TRACKS.find(t => t.track === track);
  }

  changeQuality(newQuality: VideoQuality, event: Event): void {
    event.stopPropagation();
    if (this.curr_quality !== newQuality) {
      const currentTime = this.getCurrentVideoTime();
      this.curr_quality = newQuality;
      this.setVideoSource(currentTime);
    }
  }

  changeTrack(newTrack: AudioTrack, event: Event): void {
    event.stopPropagation();
    if (this.curr_track !== newTrack) {
      this.curr_track = newTrack;
      this.setVideoSource(this.getCurrentVideoTime());
    }
  }

  setVideoSource(currentTime: number = 0): void {
    if (this.viewInitialized) {
      try {
        const videoEl = this.videoElement.nativeElement;
        const source = document.createElement('source');

        source.type = 'video/mp4';
        source.src = this.getUrl();

        videoEl.innerHTML = '';
        videoEl.appendChild(source);
        videoEl.load();
        videoEl.addEventListener('loadeddata', function () {
          const playPromise = videoEl.play();
          videoEl.currentTime = currentTime;
          if (playPromise !== undefined) {
            playPromise.then(_ => {
              // Autoplay started!
            }).catch(error => {
              console.log("Couldn't autoplay. User needs to start manually.")
            });
          }
        });
      } catch (e) {
        console.error(e);
      }
    }
  }

  emitCurrentTime() {
    const currentTime = this.getCurrentVideoTime();
    if (currentTime > 5) {
      this.storageService.setVideo(this.video as IVideo, currentTime);
      this.currentTime.emit(currentTime);
    }
  }

  getLastKnownTime(): number {
    const savedTime = this.storageService.getVideoPosition(this.video as IVideo);
    if (savedTime !== null) {
      return savedTime;
    }
    return 0;
  }

  getCurrentVideoTime(): number {
    if (!this.videoElement) {
      return 0;
    }
    return this.videoElement.nativeElement.currentTime;
  }

  getUrl(): string {
    if (!this.video) return '';
    const info = this.getTrackInfo(this.curr_track);
    return info ? info.getUrl(this.video, this.curr_quality) : '';
  }

  toggleFullscreen(): void {
    const elem = this.wrapperElement.nativeElement;

    if (!document.fullscreenElement) {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  @HostListener('document:fullscreenchange', ['$event'])
  handleFullscreen(event: Event): void {
    if (document.fullscreenElement) {
      this.showSlider = true;
    } else {
      this.showSlider = true;
    }
  }
}
