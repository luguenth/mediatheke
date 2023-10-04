import { Component, Input, ElementRef, SimpleChanges, ViewChild, OnInit, OnChanges, AfterViewInit, HostListener, EventEmitter, Output } from '@angular/core';
import { IVideo } from '../interfaces';
import { StorageService } from '../services/storage.service';

export enum VideoQuality {
  SMALL = "SD",
  BASE = "MD",
  HD = "HD"
}

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
  availableQualities: VideoQuality[] = [];
  curr_quality = VideoQuality.BASE;
  viewInitialized = false;
  showSlider = false;
  hasDescriptiveAudio = false;
  descriptiveAudioEnabled = false;

  constructor(
    private storageService: StorageService
  ) { }

  ngOnInit(): void {
    this.setVideoSource(this.getLastKnownTime());
    this.updateAvailableQualities();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.viewInitialized && changes.video && changes.video.currentValue) {
      this.video = changes.video.currentValue;
      this.updateAvailableQualities();
      this.setVideoSource(this.getLastKnownTime());
    }
  }

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    this.setVideoSource(this.urlTime !== 0 ? this.urlTime : this.getLastKnownTime());
  }

  updateAvailableQualities(): void {
    this.availableQualities = [];
    if (this.video?.url_video) {
      this.availableQualities.push(VideoQuality.BASE);
    }
    if (this.video?.url_video_low) {
      this.availableQualities.push(VideoQuality.SMALL);
    }
    if (this.video?.url_video_hd) {
      this.availableQualities.push(VideoQuality.HD);
    }
    if (this.video?.url_video_descriptive_audio !== null) {
      this.hasDescriptiveAudio = true;
    } else {
      this.hasDescriptiveAudio = false;
    }
  }



  changeQuality(newQuality: VideoQuality, event: Event): void {
    event.stopPropagation();  // Stop event bubbling to avoid video pause
    if (this.curr_quality !== newQuality) {
      const currentTime = this.getCurrentVideoTime();
      this.curr_quality = newQuality;
      this.setVideoSource(currentTime);
    }
  }

  changeAudioTrack(event: Event): void {
    event.stopPropagation();  // Stop event bubbling to avoid video pause
    this.descriptiveAudioEnabled = !this.descriptiveAudioEnabled;
    this.setVideoSource(this.getCurrentVideoTime());
  }

  setVideoSource(currentTime: number = 0): void {
    if (this.viewInitialized) {
      try {
        const videoEl = this.videoElement.nativeElement;
        const source = document.createElement('source');

        source.type = 'video/mp4';
        source.src = this.getUrl(this.curr_quality);

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
              // Show a "Play" button so the user can start manually.
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
    // only do if currentTime is bigger than 5 seconds
    if (currentTime > 5) {
      this.storageService.setVideoPosition(this.video as IVideo, currentTime);
      this.currentTime.emit(currentTime);
    }
  }

  getLastKnownTime(): number {
    const savedTime = this.storageService.getVideoPosition(this.video as IVideo);
    if (savedTime !== null) {
      return savedTime;
    }

    return 0; // Default value, you can change this
  }

  getCurrentVideoTime(): number {
    if (!this.videoElement) {
      return 0;
    }

    return this.videoElement.nativeElement.currentTime;
  }

  // Using the VideoQuality enum for better readability
  getUrl(quality: VideoQuality): string {
    if (!this.video) {
      return '';
    }

    switch (quality) {
      case VideoQuality.BASE:
        if (this.descriptiveAudioEnabled) {
          return this.video.url_video_descriptive_audio;
        }
        return this.video.url_video;

      case VideoQuality.SMALL:
        if (this.descriptiveAudioEnabled) {
          return this.video.url_video_low_descriptive_audio;
        }
        return this.video.url_video_low;

      case VideoQuality.HD:
        if (this.descriptiveAudioEnabled) {
          return this.video.url_video_hd_descriptive_audio;
        }
        return this.video.url_video_hd;

      default:
        return this.video.url_video;
    }
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

