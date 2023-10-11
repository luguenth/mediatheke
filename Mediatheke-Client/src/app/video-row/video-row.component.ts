import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { IVideo, IVideoLocalStorage, IVideoOptions } from '../interfaces';
import { BackendService } from '../services/backend';
import { options_type } from '../topics';
import { StorageService } from '../services/storage.service';

@Component({
  selector: 'app-video-row',
  templateUrl: './video-row.component.html',
  styleUrls: ['./video-row.component.scss']
})
export class VideoRowComponent implements OnInit {
  @Input() title!: string;
  @Input() description!: string;
  @Input() options!: IVideoOptions;

  videos: any[] = [];

  constructor(
    private backendService: BackendService,
    private storageService: StorageService
  ) { }

  ngOnInit(): void {
    switch (this.options.type) {
      case options_type.recommended:
        this.backendService.getAllRecommendations().subscribe(data => {
          this.videos = data;
        });
        break;
      case options_type.topic:
        this.backendService.getVideosByTopic(this.options.payload ?? "", this.options.limit ?? 10).subscribe(data => {
          this.videos = data;
        });
        break;
      case options_type.series:
        this.backendService.getAllSeries().subscribe(data => {
          this.videos = data;
        });
        break;
      case options_type.last_seen:
        const lastWatched: IVideoLocalStorage[] = this.storageService.getLastWatchedVideos(10)
        const ids = lastWatched.map(video => video.id);
        if (ids.length > 0) {
          this.backendService.getVideosByIds(ids).subscribe(data => {
            this.videos = data;
          });
        }
        break;
      default:
        break;

    }

  }
}
