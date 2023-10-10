import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoSeriesNavComponent } from './video-series-nav.component';

describe('VideoSeriesNavComponent', () => {
  let component: VideoSeriesNavComponent;
  let fixture: ComponentFixture<VideoSeriesNavComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VideoSeriesNavComponent]
    });
    fixture = TestBed.createComponent(VideoSeriesNavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
