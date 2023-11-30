import { Component, Input } from '@angular/core';
import { IVideo } from '../interfaces';

@Component({
  selector: 'app-video-small-list',
  templateUrl: './video-small-list.component.html',
  styleUrls: ['./video-small-list.component.scss']
})
export class VideoSmallListComponent {
  @Input() videos!: IVideo[];
}
