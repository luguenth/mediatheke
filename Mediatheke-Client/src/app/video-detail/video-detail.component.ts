import { Component, OnInit, OnDestroy, ChangeDetectorRef, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BackendService } from '../services/backend';
import { IVideo, ISeriesDetectionJob } from '../interfaces';
import { Subscription } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { UserService } from '../services/userService';
import { StorageService } from '../services/storage.service';
import { MediaService } from '../services/media.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-video-detail',
  templateUrl: './video-detail.component.html',
  styleUrls: ['./video-detail.component.scss']
})
export class VideoDetailComponent implements OnInit, OnDestroy {
  videoId: string = '';
  video?: IVideo;
  recommendedVideos: IVideo[] = [];
  recommendationsLoaded: boolean = false;
  seriesVideos: IVideo[] = [];
  subscriptions: Subscription[] = [];
  urlTime: number = 0;
  seriesDetectionJobs: ISeriesDetectionJob[] = [];
  detectionMethod: string = 'regex';
  env = environment;
  flaggedItems: any[] = [];
  isRecommended: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private backendService: BackendService,
    private cdr: ChangeDetectorRef,
    public userService: UserService,
    private router: Router,
    public storageService: StorageService,
    private mediaService: MediaService
  ) { }

  ngOnInit(): void {
    this.urlTime = parseInt(this.route.snapshot.queryParamMap.get('time') || '0');
    const routeSub = this.route.params.pipe(
      switchMap(params => {
        this.videoId = params['id'];
        return this.backendService.getVideo(this.videoId).pipe(
          catchError(err => {
            if (err.status === 404) {
              this.router.navigate(['/']);
            }
            throw err;
          })
        );
      })
    ).subscribe(video => {
      this.resetComponentState();
      this.video = video;
      this.cdr.detectChanges();
      this.getRecommendedVideos();
      this.triggerSeriesDetectionForAll();
      this.checkRecommendation();
    });

    this.subscriptions.push(routeSub);
    this.loadFlaggedItems();
  }

  resetComponentState() {
    this.video = undefined;
    this.recommendedVideos = [];
    this.recommendationsLoaded = false;
    this.isRecommended = false;
    this.seriesVideos = [];
    this.seriesDetectionJobs = [];
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  getRecommendedVideos() {
    const recSub = this.backendService.getRecommendedVideos(this.videoId).subscribe(data => {
      this.recommendedVideos = data;
      this.recommendationsLoaded = true;
    });

    this.subscriptions.push(recSub);
  }

  triggerSeriesDetectionForAll() {
    // Fire-and-forget: trigger detection for the main video and all its
    // recommended videos, then poll for job status for the debug view.
    this.backendService.triggerSeriesDetection(this.videoId, this.detectionMethod).subscribe({
      next: (jobs) => {
        this.seriesDetectionJobs = jobs;
        this.loadSeriesDetectionJobs();
      },
      error: (err) => console.error('Failed to trigger series detection:', err),
    });
  }

  loadSeriesDetectionJobs() {
    this.backendService.getSeriesDetectionJobs(this.videoId).subscribe({
      next: (jobs) => {
        this.seriesDetectionJobs = jobs;
        // Poll while any job is still pending/running
        const hasActive = jobs.some(j => j.state === 'pending' || j.state === 'running');
        if (hasActive) {
          setTimeout(() => this.loadSeriesDetectionJobs(), 3000);
        }
      },
      error: (err) => console.error('Failed to load series detection jobs:', err),
    });
  }

  formatJobResult(resultJson: string | null): string {
    if (!resultJson) return '—';
    try {
      const items = JSON.parse(resultJson);
      if (items.length === 0) return 'Keine Serie';
      return items.map((i: any) => `${i.series_name || '?'} S${i.season_number}E${i.episode_number}`).join(', ');
    } catch {
      return resultJson;
    }
  }

  navigateToEpisode(episode: IVideo) {
    this.router.navigate(['/video-detail', episode.id]);
  }

  checkRecommendation() {
    this.mediaService.isRecommended(this.video!).subscribe(data => {
      this.isRecommended = data;
    });
  }

  toggleRecommend() {
    this.mediaService.recommend(this.video!).subscribe(success => {
      if (success) {
        this.isRecommended = !this.isRecommended;
      }
    });
  }

  loadFlaggedItems() {
    try {
      const stored = localStorage.getItem('series-feedback');
      this.flaggedItems = stored ? JSON.parse(stored) : [];
    } catch {
      this.flaggedItems = [];
    }
  }

  flagForReview(reason: string) {
    if (!this.video) return;
    const entry = {
      id: this.video.id,
      title: this.video.title,
      topic: this.video.topic,
      channel: this.video.channel,
      series_name: this.video.series_name,
      episode_number: this.video.episode_number,
      season_number: this.video.season_number,
      url: this.video.url_website,
      reason: reason,
      timestamp: new Date().toISOString(),
    };
    // Avoid duplicates
    this.flaggedItems = this.flaggedItems.filter((f: any) => f.id !== entry.id);
    this.flaggedItems.push(entry);
    localStorage.setItem('series-feedback', JSON.stringify(this.flaggedItems));
  }

  removeFlaggedItem(id: number) {
    this.flaggedItems = this.flaggedItems.filter((f: any) => f.id !== id);
    localStorage.setItem('series-feedback', JSON.stringify(this.flaggedItems));
  }

  clearFlaggedItems() {
    this.flaggedItems = [];
    localStorage.removeItem('series-feedback');
  }

  exportFlaggedItems() {
    const json = JSON.stringify(this.flaggedItems, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `series-feedback-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

}
