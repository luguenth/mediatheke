import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BackendService } from './backend';
import { IVideo, IVideoThumbnailUrl } from '../interfaces';
import { UserService } from './userService';
import { Observable, Observer, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ISeason, ISeasonTab, ISeries } from '../video-series-nav/video-series-nav.component';

@Injectable({
  providedIn: 'root'
})
export class MediaService {

  constructor(
    private router: Router,
    private backendService: BackendService,
    private userService: UserService
  ) { }

  goToVideo(video: IVideo) {
    this.router.navigate(['/video-detail/', video.id]);
  }

  goToTopic(topic: string) {
    this.router.navigate(['/topic/', topic]);
  }

  goToChannel(video: IVideo) {
    this.router.navigate(['/channel/', video.channel]);
  }

  recommend(video: IVideo): Observable<boolean> {
    return new Observable<boolean>(observer => {
      this.userService.email$.subscribe(email => {
        if (!email) {
          observer.next(false);
          observer.complete();
          return;
        }
        this.backendService.recommend(video.id, email).pipe(
          map(() => true),
          catchError((err) => {
            console.error('Recommendation failed:', err);
            return of(false);
          })
        ).subscribe(data => {
          observer.next(data);
          observer.complete();
        });
      });
    });
  }

  isRecommended(video: IVideo): Observable<boolean> {
    return new Observable((observer: Observer<boolean>) => {
      this.userService.email$.subscribe(email => {
        if (!email) {
          observer.next(false);
          observer.complete();
          return;
        }
        this.backendService.isRecommended(video.id, email).subscribe(data => {
          observer.next(data);
          observer.complete();
        });
      });
    });
  }

  getThumbnail(video: IVideo): Observable<IVideoThumbnailUrl> {
    const urlItem: IVideoThumbnailUrl = {
      media_item_id: video.id,
      url: video.url_website
    };
    return this.backendService.getThumbnail(urlItem);
  }

  getSeriesFromEpisode(video: IVideo): Observable<ISeries> {
    return new Observable((observer: Observer<ISeries>) => {
      this.backendService.getSeriesFromEpisode(video.id).subscribe(data => {
        const series: ISeries = {
          name: video.series_name,
          seasons: this.getSeasons(data)
        };
        observer.next(series);
        observer.complete();
      });
    });
  }

  private getSeasons(seriesVideos: IVideo[]): ISeasonTab[] {
    const seasons: ISeasonTab[] = [];
    seriesVideos.forEach((video: IVideo) => {
      // Check if season already exists
      const temp_season_name = video.season_number ? video.season_number : 999;
      const seasonIndex = seasons.findIndex(s => s.season.season_number === temp_season_name);
      if (seasonIndex === -1) {
        // Season does not exist, create new season
        const season: ISeasonTab = {
          season: {
            season_number: temp_season_name,
            episodes: [video]
          },
          active: false
        };
        seasons.push(season);
      } else {
        // Season already exists, add episode to existing season
        seasons[seasonIndex].season.episodes.push(video);
      }

      // Sort episodes by episode number
      seasons.forEach(s => s.season.episodes.sort((a, b) => a.episode_number - b.episode_number));

      // Sort seasons by season number
      seasons.sort((a, b) => a.season.season_number - b.season.season_number);
    });
    return seasons;
  }

}
