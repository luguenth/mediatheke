import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BackendService } from './backend';
import { IVideo, IVideoThumbnailUrl } from '../interfaces';
import { UserService } from './userService';
import { Observable, Observer, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

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

}
