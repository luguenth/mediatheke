import { Component, Input, OnInit } from '@angular/core';
import { IVideo } from '../interfaces';
import { MediaService } from '../services/media.service';

@Component({
  selector: 'app-video-result-list',
  templateUrl: './video-result-list.component.html',
  styleUrls: ['./video-result-list.component.scss']
})
export class VideoResultListComponent implements OnInit {
  @Input() videos!: IVideo[];

  constructor(
    public mediaService: MediaService
  ) { }

  ngOnInit(): void {
  }

}
