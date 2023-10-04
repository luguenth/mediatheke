import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoResultListComponent } from './video-result-list.component';

describe('VideoResultListComponent', () => {
  let component: VideoResultListComponent;
  let fixture: ComponentFixture<VideoResultListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VideoResultListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VideoResultListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
