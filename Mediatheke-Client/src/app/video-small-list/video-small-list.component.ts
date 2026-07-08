import { Component, Input, ChangeDetectorRef } from '@angular/core';
import { IVideo } from '../interfaces';
import { MediaService } from '../services/media.service';
import { of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Component({
  selector: 'app-video-small-list',
  templateUrl: './video-small-list.component.html',
  styleUrls: ['./video-small-list.component.scss']
})
export class VideoSmallListComponent {
  @Input() videos!: IVideo[];

  private thumbnailCache = new Map<number, string>();
  private pendingThumbnails = new Set<number>();

  constructor(
    private mediaService: MediaService,
    private cdr: ChangeDetectorRef
  ) { }

  getThumbnailSrc(video: IVideo): string {
    const cached = this.thumbnailCache.get(video.id);
    if (cached !== undefined) {
      return cached;
    }
    if (video.thumbnail) {
      this.thumbnailCache.set(video.id, video.thumbnail);
      return video.thumbnail;
    }
    if (!this.pendingThumbnails.has(video.id)) {
      this.pendingThumbnails.add(video.id);
      this.mediaService.getThumbnail(video).pipe(
        map(t => t.url),
        catchError(() => of(''))
      ).subscribe(url => {
        this.thumbnailCache.set(video.id, url);
        this.pendingThumbnails.delete(video.id);
        this.cdr.markForCheck();
      });
    }
    return '';
  }

  hasThumbnail(video: IVideo): boolean {
    return !!this.getThumbnailSrc(video);
  }
}
