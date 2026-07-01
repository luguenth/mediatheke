import { Component, OnInit, Input } from '@angular/core';
import { Observable } from 'rxjs';
import { IVideoLocalStorage, IVideoOptions } from '../interfaces';
import { BackendService } from '../services/backend';
import { options_type } from '../topics';
import { StorageService } from '../services/storage.service';

@Component({
  selector: 'app-video-topic-row',
  templateUrl: './video-topic-row.component.html',
  styleUrls: ['./video-topic-row.component.scss']
})

export class VideoTopicRowComponent implements OnInit {
  @Input() title!: string;
  @Input() description!: string;
  @Input() options!: IVideoOptions;

  videos: any[] = [];

  /* how many videos to fetch per batch from the backend */
  limit = 10;
  /* number of videos already fetched (used as the skip value for the next batch) */
  skip = 0;
  /* whether a request is currently in flight */
  loading = false;
  /* whether there are likely more videos to load */
  hasMore = true;

  constructor(
    private backendService: BackendService,
    private storageService: StorageService
  ) { }

  ngOnInit(): void {
    switch (this.options.type) {
      case options_type.recommended:
        this.fetch(this.backendService.getAllRecommendations(this.skip, this.limit));
        break;
      case options_type.topic:
        this.fetch(this.backendService.getVideosByTopic(this.options.payload ?? "", this.skip, this.limit));
        break;
      case options_type.series:
        this.fetch(this.backendService.getAllSeries(this.skip, this.limit));
        break;
      case options_type.last_seen:
        // last-seen is bounded by local storage (capped at 10), so there is no "load more"
        const lastWatched: IVideoLocalStorage[] = this.storageService.getLastWatchedVideos(10);
        if (lastWatched.length === 0) {
          this.hasMore = false;
        } else {
          const ids = lastWatched.map(video => video.id);
          this.fetch(this.backendService.getVideosByIds(ids), /*pagedEnd*/ true);
        }
        this.hasMore = false;
        break;
      default:
        this.hasMore = false;
        break;
    }
  }

  loadMore(): void {
    if (this.loading || !this.hasMore) {
      return;
    }
    this.skip += this.limit;
    switch (this.options.type) {
      case options_type.recommended:
        this.fetch(this.backendService.getAllRecommendations(this.skip, this.limit));
        break;
      case options_type.topic:
        this.fetch(this.backendService.getVideosByTopic(this.options.payload ?? "", this.skip, this.limit));
        break;
      case options_type.series:
        this.fetch(this.backendService.getAllSeries(this.skip, this.limit));
        break;
      default:
        this.hasMore = false;
        break;
    }
  }

  /**
   * Fetch a batch and append its unique videos to `videos`.
   * @param pagedEnd if true, force hasMore=false regardless of batch size
   *                 (used for sources that are not paginated, e.g. last-seen).
   */
  private fetch(obs: Observable<any[]>, pagedEnd: boolean = false): void {
    this.loading = true;
    obs.subscribe(data => {
      // dedupe by id (recommended/series return random order, so later batches might overlap)
      const existing = new Set(this.videos.map((v: any) => v.id));
      for (const v of data) {
        if (!existing.has(v.id)) {
          this.videos.push(v);
          existing.add(v.id);
        }
      }
      // if we got fewer than the requested batch, we've reached the end
      this.hasMore = pagedEnd ? false : data.length >= this.limit;
      this.loading = false;
    }, () => {
      this.loading = false;
      this.hasMore = false;
    });
  }
}