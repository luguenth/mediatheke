import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VideoResultGridComponent } from './video-result-grid.component';

describe('VideoResultGridComponent', () => {
  let component: VideoResultGridComponent;
  let fixture: ComponentFixture<VideoResultGridComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VideoResultGridComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VideoResultGridComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
