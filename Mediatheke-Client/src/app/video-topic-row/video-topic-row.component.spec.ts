import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoTopicRowComponent } from './video-topic-row.component';

describe('VideoTopicRowComponent', () => {
  let component: VideoTopicRowComponent;
  let fixture: ComponentFixture<VideoTopicRowComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VideoTopicRowComponent]
    });
    fixture = TestBed.createComponent(VideoTopicRowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
