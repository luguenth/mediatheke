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
  HostListener,
} from '@angular/core';
import { Router } from '@angular/router';
import { IVideo } from '../interfaces';
import { StorageService } from '../services/storage.service';
import { MediaService } from '../services/media.service';
import {
  ISeries,
  ISeasonTab,
} from '../video-series-nav/video-series-nav.component';
import { generateThumbnails } from './thumbnails';

// Seconds before the end at which the "Up Next" autoplay overlay appears.
const NEXT_UP_THRESHOLD = 15;

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

interface ThumbEntry {
  time: number;
  dataUrl: string;
}

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
  activeSubmenu: 'quality' | 'track' | 'rate' | null = null;
  availableRates: number[] = [0.5, 0.75, 1, 1.25, 1.5, 2];
  curr_rate = 1;
  currentPlaybackTime = 0;

  // Share
  showShareMenu = false;
  shareLink = '';
  includeTimestamp = true;
  copied = false;

  thumbnails: ThumbEntry[] = [];
  thumbPreview: { src: string; time: number } | null = null;
  thumbPreviewX = 0;

  // Series navigation & autoplay (Netflix-style)
  showEpisodesMenu = false;
  $series: ISeries = { seasons: [], name: '' };
  activeEpisodesSeason: ISeasonTab | null = null;
  nextEpisode: IVideo | null = null;
  showUpNext = false;
  upNextCountdown = 0;
  upNextCancelled = false;

  constructor(
    private storageService: StorageService,
    private ngZone: NgZone,
    private mediaService: MediaService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.updateAvailableOptions();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.viewInitialized && changes.video && changes.video.currentValue) {
      this.video = changes.video.currentValue;
      this.updateAvailableOptions();
      this.loadSourceWithTime(this.getLastKnownTime());
      this.startThumbGen();
      this.loadSeries();
    }
  }

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    const startTime =
      this.urlTime !== 0 ? this.urlTime : this.getLastKnownTime();
    this.loadSourceWithTime(startTime);
    this.startThumbGen();
    this.loadSeries();
  }

  get videoElement(): HTMLVideoElement | null {
    return this.videoEl?.nativeElement ?? null;
  }

  private startThumbGen(): void {
    this.thumbnails = [];
    this.thumbPreview = null;
    if (!this.video) return;
    const duration = this.video.duration || 0;
    if (duration < 10) return;
    const url = this.getUrl();
    if (!url) return;

    generateThumbnails(url, duration).then((frames) => {
      this.thumbnails = frames;
    });
  }

  onTimelineHover(event: MouseEvent): void {
    const wrapper = event.currentTarget as HTMLElement;
    const slider = wrapper.querySelector('media-time-slider');
    if (!slider) return;

    const rect = slider.getBoundingClientRect();
    const pct = Math.max(
      0,
      Math.min(1, (event.clientX - rect.left) / rect.width),
    );
    if (!this.video || !this.video.duration) return;

    const time = pct * this.video.duration;
    this.thumbPreviewX = event.clientX - wrapper.getBoundingClientRect().left;

    const nearest = this.findNearestThumbnail(time);
    this.thumbPreview = nearest
      ? { src: nearest.dataUrl, time: nearest.time }
      : { src: '', time };
  }

  onTimelineLeave(): void {
    this.thumbPreview = null;
  }

  private findNearestThumbnail(time: number): ThumbEntry | null {
    if (this.thumbnails.length === 0) return null;
    let best = this.thumbnails[0];
    let bestDiff = Math.abs(best.time - time);
    for (const t of this.thumbnails) {
      const diff = Math.abs(t.time - time);
      if (diff < bestDiff) {
        bestDiff = diff;
        best = t;
      }
    }
    return best;
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

  changeRate(rate: number): void {
    if (this.curr_rate !== rate) {
      this.curr_rate = rate;
      const el = this.videoElement;
      if (el) el.playbackRate = rate;
    }
    this.showMenu = false;
    this.activeSubmenu = null;
  }

  rateLabel(rate: number): string {
    return `${rate}×`;
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
        playPromise.catch(() => {});
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
    if (!savedTime) return 0;
    // If the saved position is within the up-next threshold of the end,
    // the video was (almost) fully watched — start over next time.
    const duration = this.video?.duration || 0;
    if (duration > 0 && duration - savedTime <= NEXT_UP_THRESHOLD) {
      return 0;
    }
    return savedTime;
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
    this.showEpisodesMenu = false;
    this.showShareMenu = false;
  }

  toggleShareMenu(event: Event): void {
    event.stopPropagation();
    this.showShareMenu = !this.showShareMenu;
    if (this.showShareMenu) this.generateShareLink();
    this.showMenu = false;
    this.activeSubmenu = null;
    this.showEpisodesMenu = false;
  }

  generateShareLink(): void {
    const url = window.location.href.split('?')[0];
    this.shareLink = this.includeTimestamp
      ? `${url}?time=${Math.floor(this.currentPlaybackTime)}`
      : url;
  }

  toggleTimestamp(): void {
    this.generateShareLink();
  }

  copyToClipboard(): void {
    navigator.clipboard.writeText(this.shareLink).then(() => {
      this.copied = true;
      setTimeout(() => (this.copied = false), 1500);
    });
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.showMenu && !this.showEpisodesMenu && !this.showShareMenu) return;
    const target = event.target as HTMLElement | null;
    if (!target) return;
    const root = this.wrapperElement?.nativeElement;
    const sourceWrap = root?.querySelector('.vjs-source-wrap');
    if (this.showMenu && sourceWrap && !sourceWrap.contains(target)) {
      this.showMenu = false;
      this.activeSubmenu = null;
    }
    const shareWrap = root?.querySelector('.vjs-share-wrap');
    if (this.showShareMenu && shareWrap && !shareWrap.contains(target)) {
      this.showShareMenu = false;
    }
    const episodesWrap = root?.querySelector('.vjs-episodes-wrap');
    const episodesPanel = root?.querySelector('.vjs-episodes-menu');
    if (
      this.showEpisodesMenu &&
      episodesWrap &&
      !episodesWrap.contains(target) &&
      !(episodesPanel && episodesPanel.contains(target))
    ) {
      this.showEpisodesMenu = false;
    }
  }

  formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  // ── Series navigation & autoplay (Netflix-style) ──

  toggleEpisodesMenu(event: Event): void {
    event.stopPropagation();
    this.showEpisodesMenu = !this.showEpisodesMenu;
    this.showMenu = false;
    this.activeSubmenu = null;
    this.showShareMenu = false;
  }

  selectEpisodesSeason(season: ISeasonTab): void {
    this.activeEpisodesSeason = season;
  }

  isCurrentEpisode(episode: IVideo): boolean {
    return !!this.video && episode.id === this.video.id;
  }

  navigateToEpisode(episode: IVideo): void {
    this.showEpisodesMenu = false;
    this.router.navigate(['/video-detail', episode.id]);
  }

  playNextNow(): void {
    if (this.nextEpisode) {
      this.navigateToEpisode(this.nextEpisode);
    }
  }

  cancelUpNext(): void {
    this.showUpNext = false;
    this.upNextCancelled = true;
  }

  onVideoEnded(): void {
    if (this.nextEpisode && !this.upNextCancelled) {
      this.navigateToEpisode(this.nextEpisode);
    }
  }

  onTimeUpdate(): void {
    this.currentPlaybackTime = this.getCurrentVideoTime();
    this.emitCurrentTime();
    this.checkUpNext();
  }

  private checkUpNext(): void {
    if (!this.nextEpisode || this.upNextCancelled) {
      this.showUpNext = false;
      return;
    }
    const el = this.videoElement;
    if (!el || !el.duration || !isFinite(el.duration)) return;
    const remaining = el.duration - el.currentTime;
    if (remaining <= NEXT_UP_THRESHOLD && remaining > 0.2) {
      this.showUpNext = true;
      this.upNextCountdown = Math.ceil(remaining);
    } else if (remaining > NEXT_UP_THRESHOLD) {
      this.showUpNext = false;
    }
  }

  private loadSeries(): void {
    this.$series = { seasons: [], name: this.video?.series_name || '' };
    this.activeEpisodesSeason = null;
    this.nextEpisode = null;
    this.showUpNext = false;
    this.upNextCancelled = false;
    if (!this.video?.series_name) return;
    this.mediaService.getSeriesFromEpisode(this.video).subscribe((series) => {
      this.$series = series;
      this.activeEpisodesSeason =
        this.findCurrentSeason() ?? series.seasons[0] ?? null;
      this.nextEpisode = this.computeNextEpisode();
    });
  }

  private findCurrentSeason(): ISeasonTab | null {
    const sn = this.video?.season_number ? this.video.season_number : 999;
    return this.$series.seasons.find(
      (s) => s.season.season_number === sn,
    ) ?? null;
  }

  private computeNextEpisode(): IVideo | null {
    const flat: IVideo[] = [];
    const sortedSeasons = [...this.$series.seasons].sort(
      (a, b) => a.season.season_number - b.season.season_number,
    );
    for (const s of sortedSeasons) {
      const eps = [...s.season.episodes].sort(
        (a, b) => a.episode_number - b.episode_number,
      );
      flat.push(...eps);
    }
    const idx = flat.findIndex((v) => v.id === this.video?.id);
    return idx >= 0 && idx + 1 < flat.length ? flat[idx + 1] : null;
  }
}
