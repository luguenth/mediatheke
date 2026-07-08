import { Component } from '@angular/core';
import { SearchService } from '../services/search.service';
import { MediaService } from '../services/media.service';
import { IVideo } from '../interfaces';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Component({
  selector: 'app-video-search-results',
  templateUrl: './video-search-results.component.html',
  styleUrls: ['./video-search-results.component.scss']
})
export class VideoSearchResultsComponent {
  constructor(
    public searchService: SearchService,
    private mediaService: MediaService
  ) { }

  getThumbnail(video: IVideo): Observable<string> {
    if (video.thumbnail) {
      return of(video.thumbnail);
    }
    return this.mediaService.getThumbnail(video).pipe(
      map(t => t.url),
      catchError(() => of(''))
    );
  }
}
