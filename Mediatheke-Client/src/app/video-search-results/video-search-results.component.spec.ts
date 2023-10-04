import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoSearchResultsComponent } from './video-search-results.component';

describe('VideoSearchResultsComponent', () => {
  let component: VideoSearchResultsComponent;
  let fixture: ComponentFixture<VideoSearchResultsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VideoSearchResultsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VideoSearchResultsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
