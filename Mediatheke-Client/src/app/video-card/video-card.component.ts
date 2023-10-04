import { Component, Input, ElementRef, Renderer2, OnInit, AfterViewInit } from '@angular/core';
import { IVideo } from '../interfaces';
import { UserService } from '../services/userService';
import { MediaService } from '../services/media.service';
import { StorageService } from '../services/storage.service';

@Component({
  selector: 'app-video-card',
  templateUrl: './video-card.component.html',
  styleUrls: ['./video-card.component.scss']
})
export class VideoCardComponent implements OnInit {
  @Input() video!: IVideo;
  @Input() details: boolean = true;  // default value
  public backgroundColor: string = 'initial';  // default value
  public imgSrc: string = '';

  constructor(
    private el: ElementRef,
    private renderer: Renderer2,
    public userService: UserService,
    public mediaService: MediaService,
    public storageService: StorageService,
  ) {
  }

  ngOnInit() {
    if (this.video.thumbnail) {
      this.imgSrc = this.video.thumbnail;
    } else {
      this.mediaService.getThumbnail(this.video).subscribe(thumbnail => {
        this.imgSrc = thumbnail.url;
      });
    }
  }


  handleImageError() {
    this.updateBackgroundColor();
    //this.replaceImageWithErrorElement();
  }

  updateBackgroundColor() {
    this.backgroundColor = '#' + Math.floor((Math.random() * 0xFFFFFF)).toString(16);
  }

  replaceImageWithErrorElement() {
    const errorElement = this.renderer.createElement('div');
    this.renderer.addClass(errorElement, 'videocard__image-error');
    const text = this.renderer.createText('Still generating thumbnail...');
    this.renderer.appendChild(errorElement, text);
    this.renderer.appendChild(this.el.nativeElement, errorElement);
  }

}
