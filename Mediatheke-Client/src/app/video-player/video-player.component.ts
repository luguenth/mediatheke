import {
  Component,
  Input,
  ElementRef,
  SimpleChanges,
  ViewChild,
  OnInit,
  OnChanges,
  AfterViewInit,
  Output,
  EventEmitter,
  NgZone,
} from '@angular/core';
import { IVideo } from '../interfaces';
import { StorageService } from '../services/storage.service';

export enum VideoQuality {
  SMALL = 'SD',
  BASE = 'MD',
  HD = 'HD',
}

export enum AudioTrack {
  REGULAR = 'DE',
  AD = 'AD',
  UT = 'UT',
  OV = 'OV',
  OV_UT = 'OV+UT',
}

interface TrackInfo {
  track: AudioTrack;
  label: string;
  verbose: string;
  hasUrls: (v: IVideo) => boolean;
  getUrl: (v: IVideo, quality: VideoQuality) => string;
}

const TRACKS: TrackInfo[] = [
  {
    track: AudioTrack.REGULAR,
    label: 'DE',
    verbose: 'Deutsch',
    hasUrls: (v) => !!v.url_video,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL:
          return v.url_video_low;
        case VideoQuality.HD:
          return v.url_video_hd;
        default:
          return v.url_video;
      }
    },
  },
  {
    track: AudioTrack.AD,
    label: 'AD',
    verbose: 'Deutsch (Audiodeskription)',
    hasUrls: (v) => !!v.url_video_descriptive_audio,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL:
          return v.url_video_low_descriptive_audio;
        case VideoQuality.HD:
          return v.url_video_hd_descriptive_audio;
        default:
          return v.url_video_descriptive_audio;
      }
    },
  },
  {
    track: AudioTrack.UT,
    label: 'UT',
    verbose: 'Deutsch (Untertitel)',
    hasUrls: (v) => !!v.url_video_ut,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL:
          return v.url_video_low_ut;
        case VideoQuality.HD:
          return v.url_video_hd_ut;
        default:
          return v.url_video_ut;
      }
    },
  },
  {
    track: AudioTrack.OV,
    label: 'OV',
    verbose: 'Originalton',
    hasUrls: (v) => !!v.url_video_ov,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL:
          return v.url_video_low_ov;
        case VideoQuality.HD:
          return v.url_video_hd_ov;
        default:
          return v.url_video_ov;
      }
    },
  },
  {
    track: AudioTrack.OV_UT,
    label: 'OV+UT',
    verbose: 'Originalton (mit Untertitel)',
    hasUrls: (v) => !!v.url_video_ov_ut,
    getUrl: (v, q) => {
      switch (q) {
        case VideoQuality.SMALL:
          return v.url_video_low_ov_ut;
        case VideoQuality.HD:
          return v.url_video_hd_ov_ut;
        default:
          return v.url_video_ov_ut;
      }
    },
  },
];

const QUALITY_LABELS: Record<VideoQuality, string> = {
  [VideoQuality.SMALL]: 'Niedrig (SD)',
  [VideoQuality.BASE]: 'Mittel (MD)',
  [VideoQuality.HD]: 'Hoch (HD)',
};

@Component({
  selector: 'app-video-player',
  templateUrl: './video-player.component.html',
  styleUrls: ['./video-player.component.scss'],
})
export class VideoPlayerComponent
  implements OnInit, OnChanges, AfterViewInit
{
  @Input() video: IVideo | undefined;
  @Input() urlTime: number = 0;
  @Output() currentTime = new EventEmitter<number>();
  @ViewChild('videoEl', { static: false }) videoEl!: ElementRef<HTMLVideoElement>;
  @ViewChild('wrapperElement') wrapperElement!: ElementRef;

  QualityEnum = VideoQuality;
  AudioTrackEnum = AudioTrack;
  availableQualities: VideoQuality[] = [];
  availableTracks: AudioTrack[] = [];
  curr_quality = VideoQuality.BASE;
  curr_track = AudioTrack.REGULAR;
  viewInitialized = false;
  showMenu = false;
  activeSubmenu: 'quality' | 'track' | null = null;

  constructor(
    private storageService: StorageService,
    private ngZone: NgZone,
  ) {}

  ngOnInit(): void {
    this.updateAvailableOptions();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.viewInitialized && changes.video && changes.video.currentValue) {
      this.video = changes.video.currentValue;
      this.updateAvailableOptions();
      this.loadSourceWithTime(this.getLastKnownTime());
    }
  }

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    const startTime =
      this.urlTime !== 0 ? this.urlTime : this.getLastKnownTime();
    this.loadSourceWithTime(startTime);
  }

  get videoElement(): HTMLVideoElement | null {
    return this.videoEl?.nativeElement ?? null;
  }

  updateAvailableOptions(): void {
    if (!this.video) return;
    this.availableQualities = [];
    if (this.video.url_video) this.availableQualities.push(VideoQuality.BASE);
    if (this.video.url_video_low)
      this.availableQualities.push(VideoQuality.SMALL);
    if (this.video.url_video_hd)
      this.availableQualities.push(VideoQuality.HD);

    this.availableTracks = TRACKS.filter((t) =>
      t.hasUrls(this.video!),
    ).map((t) => t.track);

    if (!this.availableTracks.includes(this.curr_track)) {
      this.curr_track = AudioTrack.REGULAR;
    }
  }

  getTrackInfo(track: AudioTrack): TrackInfo | undefined {
    return TRACKS.find((t) => t.track === track);
  }

  qualityLabel(quality: VideoQuality): string {
    return QUALITY_LABELS[quality] ?? quality;
  }

  trackLabel(track: AudioTrack): string {
    return this.getTrackInfo(track)?.verbose ?? track;
  }

  getTrackLabel(track: AudioTrack): string {
    return this.getTrackInfo(track)?.label ?? track;
  }

  changeQuality(quality: VideoQuality): void {
    if (this.curr_quality !== quality) {
      const currentTime = this.getCurrentVideoTime();
      this.curr_quality = quality;
      this.loadSourceWithTime(currentTime);
      this.showMenu = false;
      this.activeSubmenu = null;
    }
  }

  changeTrack(track: AudioTrack): void {
    if (this.curr_track !== track) {
      this.curr_track = track;
      this.loadSourceWithTime(this.getCurrentVideoTime());
      this.showMenu = false;
      this.activeSubmenu = null;
    }
  }

  getUrl(): string {
    if (!this.video) return '';
    const info = this.getTrackInfo(this.curr_track);
    return info ? info.getUrl(this.video, this.curr_quality) : '';
  }

  loadSourceWithTime(currentTime: number = 0): void {
    const videoEl = this.videoElement;
    if (!videoEl) return;

    const url = this.getUrl();
    if (!url) return;

    const handleLoaded = () => {
      videoEl.currentTime = currentTime;
      videoEl.removeEventListener('loadeddata', handleLoaded);
      const playPromise = videoEl.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          // Autoplay blocked, user needs to interact
        });
      }
    };

    videoEl.addEventListener('loadeddata', handleLoaded);
    videoEl.src = url;
    videoEl.load();
  }

  emitCurrentTime(): void {
    const currentTime = this.getCurrentVideoTime();
    if (currentTime > 5) {
      this.storageService.setVideo(this.video as IVideo, currentTime);
      this.ngZone.run(() => this.currentTime.emit(currentTime));
    }
  }

  getLastKnownTime(): number {
    const savedTime = this.storageService.getVideoPosition(
      this.video as IVideo,
    );
    return savedTime ?? 0;
  }

  getCurrentVideoTime(): number {
    return this.videoElement?.currentTime ?? 0;
  }

  toggleMenu(event: Event): void {
    event.stopPropagation();
    this.showMenu = !this.showMenu;
    if (!this.showMenu) {
      this.activeSubmenu = null;
    }
  }

  onMenuMouseLeave(event: MouseEvent): void {
    // Only close if the mouse actually left the entire menu area
    const target = event.relatedTarget as HTMLElement | null;
    const current = event.currentTarget as HTMLElement;
    if (target && current.contains(target)) {
      return;
    }
    this.showMenu = false;
    this.activeSubmenu = null;
  }
}
