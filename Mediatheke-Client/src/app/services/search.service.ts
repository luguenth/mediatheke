import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { take, catchError, map, tap, startWith } from 'rxjs/operators';
import { IVideo } from '../interfaces';
import { BackendService } from './backend';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  search?: string;
  suggestions$!: Observable<IVideo[]>;
  errorMessage?: string;
  inputFocused: boolean = false;
  public isSearching: boolean = false;

  constructor(private backendService: BackendService) { }

  ngOnInit(): void {
    this.suggestions$ = of([]);  // initialize with empty array
  }

  searchVideos(query: string = ""): void {
    if (query && query.length > 1) {
      this.isSearching = true;
      this.suggestions$ = this.backendService.searchVideos(query).pipe(
        map(response => response || []),
        startWith([]), // emit an empty array as the initial value
        tap(() => this.isSearching = false),
        catchError(err => {
          this.errorMessage = err && err.message || 'Something went wrong';
          this.isSearching = false;
          return of([]);
        })
      );
    } else {
      this.suggestions$ = of([]);
      this.isSearching = false; // reset search state when query is empty or too short
    }
  }
}
