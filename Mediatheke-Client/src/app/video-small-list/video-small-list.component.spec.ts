import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoSmallListComponent } from './video-small-list.component';

describe('VideoSmallListComponent', () => {
  let component: VideoSmallListComponent;
  let fixture: ComponentFixture<VideoSmallListComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VideoSmallListComponent]
    });
    fixture = TestBed.createComponent(VideoSmallListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
