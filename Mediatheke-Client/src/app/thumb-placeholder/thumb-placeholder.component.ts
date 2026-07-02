import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-thumb-placeholder',
  templateUrl: './thumb-placeholder.component.html',
  styleUrls: ['./thumb-placeholder.component.scss']
})
export class ThumbPlaceholderComponent {
  /** pick a value per card (e.g. video.id) so adjacent cards look different */
  @Input() variant = 0;

  private readonly bgs = [
    'var(--color-key-magenta)',
    'var(--color-key-yellow)',
    'var(--color-key-cyan)'
  ];
  private readonly symbols = ['/assets/hero/media.svg', '/assets/hero/theke.svg'];
  private readonly rotations = [0, 90, 45];
  // per-variant symbol placements: width, horizontal %, vertical %
  private readonly placements = [
    { w: 90,  x: 50, y: 50 },
    { w: 140, x: 20, y: 30 },
    { w: 70,  x: 75, y: 70 },
    { w: 110, x: 60, y: 25 },
    { w: 160, x: 45, y: 75 },
    { w: 80,  x: 25, y: 60 }
  ];

  private pick<T>(arr: T[]): T {
    return arr[this.variant % arr.length];
  }

  get bg(): string { return this.pick(this.bgs); }
  get symbol(): string { return this.pick(this.symbols); }
  get rotation(): number { return this.pick(this.rotations); }
  get placement() { return this.pick(this.placements); }
}