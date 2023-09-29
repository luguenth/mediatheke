import { Component, OnInit } from '@angular/core';
import { BackendService } from '../services/backend';
import { ActivatedRoute } from '@angular/router';
import { IVideo } from '../interfaces';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-topic-detail',
  templateUrl: './topic-detail.component.html',
  styleUrls: ['./topic-detail.component.scss']
})
export class TopicDetailComponent implements OnInit {
  topic: string = '';
  videos$!: Observable<IVideo[]>;

  constructor(
    private route: ActivatedRoute,
    private backendService: BackendService) { }

  ngOnInit(): void {
    this.topic = this.route.snapshot.paramMap.get('topicName') || '';
    this.videos$ = this.backendService.getVideosByTopic(this.topic);
  }

}
