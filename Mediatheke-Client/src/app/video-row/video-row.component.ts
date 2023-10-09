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

    /* if (this.topic) {
      if (this.topic === "serien") {
        this.backendService.getAllSeries().subscribe(data => {
          this.videos = data;
        }
        );
      } else {
        this.backendService.getVideosByTopic(this.topic).subscribe(data => {
          this.videos = data;
        });
      }
    } else {
      this.backendService.getAllRecommendations().subscribe(data => {
        this.videos = data;
      });
    } */

    switch (this.options.type) {
      case options_type.recommended:
        this.backendService.getAllRecommendations().subscribe(data => {
          this.videos = data;
        });
        break;
      case options_type.topic:
        this.backendService.getVideosByTopic(this.options.payload ?? ""
        ).subscribe(data => {
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
        console.debug(lastWatched);
        this.backendService.getVideosByIds(lastWatched.map(video => video.id)).subscribe(data => {
          this.videos = data;
        });
        break;
      default:
        break;

    }

  }
}
