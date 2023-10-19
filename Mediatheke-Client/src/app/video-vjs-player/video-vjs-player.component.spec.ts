import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoVjsPlayerComponent } from './video-vjs-player.component';

describe('VideoVjsPlayerComponent', () => {
  let component: VideoVjsPlayerComponent;
  let fixture: ComponentFixture<VideoVjsPlayerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VideoVjsPlayerComponent]
    });
    fixture = TestBed.createComponent(VideoVjsPlayerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
