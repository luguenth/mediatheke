import { Component, ElementRef, ViewChild, OnDestroy } from '@angular/core';
import { SearchService } from '../services/search.service';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-video-search',
  templateUrl: './video-search.component.html',
  styleUrls: ['./video-search.component.scss']
})
export class VideoSearchComponent implements OnDestroy {
  @ViewChild('searchInput', { static: false }) searchInput!: ElementRef;

  search: string = '';
  inputFocused: boolean = false;
  blurTimeout: ReturnType<typeof setTimeout> | null = null;

  private searchSubject = new Subject<string>();
  private searchSub: Subscription;

  constructor(public searchService: SearchService) {
    this.searchSub = this.searchSubject.pipe(
      debounceTime(250),
      distinctUntilChanged()
    ).subscribe(query => {
      this.searchService.searchVideos(query);
    });
  }

  ngOnDestroy() {
    this.searchSub.unsubscribe();
  }

  onInput(query: string): void {
    if (query.length >= 2) {
      this.searchSubject.next(query);
    } else {
      this.searchService.clear();
    }
  }

  onFocus(): void {
    if (this.blurTimeout) {
      clearTimeout(this.blurTimeout);
      this.blurTimeout = null;
    }
    this.inputFocused = true;
  }

  onBlur(): void {
    this.blurTimeout = setTimeout(() => {
      this.inputFocused = false;
    }, 200);
  }

  focusInput(): void {
    this.searchInput.nativeElement.focus();
  }

  get showDropdown(): boolean {
    return this.inputFocused && this.search.length >= 2;
  }
}
