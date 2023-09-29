import { Component, Input, OnInit } from '@angular/core';
import { IVideo } from 'src/app/interfaces';
import { MediaService } from 'src/app/services/media.service';
import { UserService } from 'src/app/services/userService';

@Component({
  selector: 'app-recommend',
  templateUrl: './recommend.component.html',
  styleUrls: ['./recommend.component.scss'],
})
export class RecommendComponent implements OnInit {
  @Input() video!: IVideo;
  @Input() isEmbedded: boolean = false;
  public userRole: string = '';
  isRecommended: boolean = false;

  constructor(
    public userService: UserService,
    public mediaService: MediaService
  ) {
  }

  ngOnInit() {
    this.mediaService.isRecommended(this.video).subscribe(data => {
      this.isRecommended = data;
    });
    this.userService.role$.subscribe(role => {
      this.userRole = role || '';
    });
  }

  toggleRecommendation(): void {
    this.mediaService.recommend(this.video).subscribe(success => {
      if (success) {
        // Toggle the recommendation state for instant feedback
        this.isRecommended = !this.isRecommended;
      } else {
        console.log('Failed to recommend');
      }
    });
  }

}
