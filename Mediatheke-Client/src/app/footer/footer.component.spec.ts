import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { FooterComponent } from './footer.component';
import { BackendService } from '../services/backend';

describe('FooterComponent', () => {
  let component: FooterComponent;
  let fixture: ComponentFixture<FooterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [FooterComponent],
      providers: [
        {
          provide: BackendService,
          useValue: { getLastFilmlisteImport: () => of({ timestamp: null, full_import: null, success: null }) }
        }
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});