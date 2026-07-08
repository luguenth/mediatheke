import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { IVideo } from '../interfaces';
import { BackendService } from './backend';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private suggestionsSubject = new BehaviorSubject<IVideo[]>([]);
  suggestions$: Observable<IVideo[]> = this.suggestionsSubject.asObservable();
  public isSearching: boolean = false;

  constructor(private backendService: BackendService) { }

  searchVideos(query: string): void {
    if (!query || query.length < 2) {
      this.clear();
      return;
    }

    this.isSearching = true;
    this.backendService.searchVideos(query).pipe(
      map(response => response || []),
      tap(() => this.isSearching = false),
      catchError(() => {
        this.isSearching = false;
        return of([]);
      })
    ).subscribe(results => {
      this.suggestionsSubject.next(results);
    });
  }

  clear(): void {
    this.suggestionsSubject.next([]);
    this.isSearching = false;
  }
}
