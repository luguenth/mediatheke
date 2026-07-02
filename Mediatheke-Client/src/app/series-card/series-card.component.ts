import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { IVideo } from '../interfaces';
import { MediaService } from '../services/media.service';

@Component({
  selector: 'app-series-card',
  templateUrl: './series-card.component.html',
  styleUrls: ['./series-card.component.scss']
})
export class SeriesCardComponent implements OnInit, OnDestroy {
  @Input() episodes: IVideo[] = [];

  name = '';
  topic = '';
  // episodes that actually carry a thumbnail url — these participate in the slideshow
  slides: IVideo[] = [];
  activeIndex = 0;
  failedCount = 0;
  private failedSlides = new Set<number>();

  private timer: any;
  private readonly intervalMs = 10000;

  constructor(public mediaService: MediaService) { }

  ngOnInit(): void {
    if (!this.episodes || this.episodes.length === 0) {
      return;
    }
    const first = this.episodes[0];
    this.name = first.series_name || first.title;
    this.topic = first.topic;

    this.slides = this.episodes.filter(v => !!v.thumbnail);

    // if none of the episodes carry a thumbnail yet, fetch the first one's
    // (mirrors the behaviour of app-video-card)
    if (this.slides.length === 0 && first) {
      this.mediaService.getThumbnail(first).subscribe(thumb => {
        if (thumb?.url) {
          const firstSlide = { ...first, thumbnail: thumb.url };
          this.slides = [firstSlide];
        }
      });
      return;
    }

    if (this.slides.length > 1) {
      // each card starts the slideshow on a different beat so the rows
      // don't all cross-fade in sync
      this.activeIndex = Math.floor(Math.random() * this.slides.length);
      const initialDelay = Math.random() * this.intervalMs;
      // first swap is staggered; afterwards a steady interval ticks
      setTimeout(() => {
        this.tick();
        this.timer = setInterval(() => this.tick(), this.intervalMs);
      }, initialDelay);
    }
  }

  private tick(): void {
    this.activeIndex = (this.activeIndex + 1) % this.slides.length;
  }

  onSlideError(i: number): void {
    if (!this.failedSlides.has(i)) {
      this.failedSlides.add(i);
      this.failedCount++;
    }
  }

  open(): void {
    if (this.episodes.length > 0) {
      this.mediaService.goToVideo(this.episodes[0]);
    }
  }

  goToTopic(event: Event): void {
    event.stopPropagation();
    if (this.episodes.length > 0) {
      this.mediaService.goToTopic(this.episodes[0].topic);
    }
  }

  ngOnDestroy(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}