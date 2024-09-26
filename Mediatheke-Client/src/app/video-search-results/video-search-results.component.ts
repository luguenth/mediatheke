import { Component, OnInit, Output } from '@angular/core';
import { SearchService } from '../services/search.service';
import { Observable } from 'rxjs';
import { IVideo } from '../interfaces';

@Component({
  selector: 'app-video-search-results',
  templateUrl: './video-search-results.component.html',
  styleUrls: ['./video-search-results.component.scss']
})
export class VideoSearchResultsComponent implements OnInit {

  constructor(
    public searchService: SearchService
  ) { }

  ngOnInit(): void {
  }

}
