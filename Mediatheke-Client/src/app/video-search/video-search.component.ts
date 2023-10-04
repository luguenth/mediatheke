import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';
import { SearchService } from '../services/search.service';
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';


@Component({
  selector: 'app-video-search',
  templateUrl: './video-search.component.html',
  styleUrls: ['./video-search.component.scss']
})
export class VideoSearchComponent implements OnInit {
  @ViewChild('searchInput', { static: false }) searchInput!: ElementRef;
  search?: string;
  inputFocused: boolean = false;

  private searchSubject: Subject<string> = new Subject();

  constructor(public searchService: SearchService) {
    // Initialize debouncing
    this.searchSubject.pipe(
      debounceTime(300)  // Set the debounce time (in milliseconds)
    ).subscribe(searchTextValue => {
      this.searchService.searchVideos(searchTextValue);
    });
  }

  ngOnInit(): void {
  }

  searchVideo(query: string = ""): void {
    this.searchSubject.next(query);  // Use next() to trigger the Subject
  }

  focusInput(): void {
    this.searchInput.nativeElement.focus();
  }
}
