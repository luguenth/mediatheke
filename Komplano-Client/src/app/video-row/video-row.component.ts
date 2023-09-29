import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { IVideo } from '../interfaces';
import { BackendService } from '../services/backend';

@Component({
  selector: 'app-video-row',
  templateUrl: './video-row.component.html',
  styleUrls: ['./video-row.component.scss']
})
export class VideoRowComponent implements OnInit {
  @Input() title!: string;
  @Input() description!: string;
  @Input() topic?: string;

  videos: any[] = [];

  constructor(private backendService: BackendService) { }

  ngOnInit(): void {
    if (this.topic) {
      this.backendService.getVideosByTopic(this.topic).subscribe(data => {
        this.videos = data;
      });
    } else {
      this.backendService.getAllRecommendations().subscribe(data => {
        this.videos = data;
      });
    }
  }
}
