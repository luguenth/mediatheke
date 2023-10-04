import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { IVideo } from '../interfaces';

@Component({
  selector: 'app-video-result-grid',
  templateUrl: './video-result-grid.component.html',
  styleUrls: ['./video-result-grid.component.scss']
})
export class VideoResultGridComponent implements OnInit {
  @Input() videos!: IVideo[];

  constructor() { }

  ngOnInit(): void {
  }

}
