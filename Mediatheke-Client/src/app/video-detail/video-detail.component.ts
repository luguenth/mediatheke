import { Component, OnInit, OnDestroy, ChangeDetectorRef, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BackendService } from '../services/backend';
import { IVideo } from '../interfaces';
import { Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { UserService } from '../services/userService';
import { StorageService } from '../services/storage.service';

@Component({
  selector: 'app-video-detail',
  templateUrl: './video-detail.component.html',
  styleUrls: ['./video-detail.component.scss']
})
export class VideoDetailComponent implements OnInit, OnDestroy {
  videoId: string = '';
  video?: IVideo;
  recommendedVideos: IVideo[] = [];
  seriesVideos: IVideo[] = [];
  subscriptions: Subscription[] = [];
  currentTime: number = 0;
  urlTime: number = 0;
  isSeries: boolean = false;
  isSeriesLoading: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private backendService: BackendService,
    private cdr: ChangeDetectorRef,
    public userService: UserService,
    private router: Router,
    public storageService: StorageService
  ) { }

  ngOnInit(): void {
    this.urlTime = parseInt(this.route.snapshot.queryParamMap.get('time') || '0');
    const routeSub = this.route.params.pipe(
      switchMap(params => {
        this.videoId = params['id'];
        return this.backendService.getVideo(this.videoId);
      })
    ).subscribe(video => {
      this.resetComponentState();
      this.video = video;
      this.cdr.detectChanges();
      this.getRecommendedVideos();
      this.getSeriesVideos();
    });

    this.subscriptions.push(routeSub);
  }

  setCurrentTime(time: number) {
    this.currentTime = time;
  }

  resetComponentState() {
    this.video = undefined;
    this.recommendedVideos = [];
    this.seriesVideos = [];
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  getRecommendedVideos() {
    const recSub = this.backendService.getRecommendedVideos(this.videoId).subscribe(data => {
      this.recommendedVideos = data;
    });

    this.subscriptions.push(recSub);
  }

  getSeriesVideos() {
    const seriesSub = this.backendService.getSeriesFromEpisode(this.videoId).subscribe(data => {
      this.seriesVideos = data.sort((a, b) => {
        if (a.season_number !== b.season_number) {
          return a.season_number - b.season_number;
        }
        return a.episode_number - b.episode_number;
      });
    });

    this.subscriptions.push(seriesSub);
  }


  mightBeASeries() {
    this.isSeriesLoading = true;
    this.backendService.mightBeASeries(this.videoId).subscribe(data => {
      this.seriesVideos = data.sort((a, b) => {
        if (a.season_number !== b.season_number) {
          return a.season_number - b.season_number;
        }
        this.isSeriesLoading = false;
        return a.episode_number - b.episode_number;
      });
    });
  }

  navigateToEpisode(episode: IVideo) {
    this.router.navigate(['/video-detail', episode.id]);
  }

}
