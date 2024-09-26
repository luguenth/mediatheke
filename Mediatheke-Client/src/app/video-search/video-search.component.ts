import { Component, ElementRef, ViewChild, OnInit, ChangeDetectorRef } from '@angular/core';
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

  constructor(
    public searchService: SearchService,
    private cdRef: ChangeDetectorRef  // Inject ChangeDetectorRef
  ) {
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
    this.cdRef.detectChanges();  // Trigger change detection
  }

  focusInput(): void {
    this.searchInput.nativeElement.focus();
  }

  handleInputBlur() {
    // Delay setting inputFocused to false to allow time for click events on search results to be processed
    // TODO: With Angular's HostListener, you can listen for clicks on the entire document and then decide whether to keep the results displayed or not.
    setTimeout(() => this.inputFocused = false, 200); // delay in milliseconds
  }
}
