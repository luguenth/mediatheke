import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-share',
  templateUrl: './share.component.html',
  styleUrls: ['./share.component.scss']
})
export class ShareComponent implements OnInit {

  @Input() currentTime: number = 0;
  @Input() variant: 'full' | 'icon' = 'full';
  shareLink: string = '';
  includeTimestamp: boolean = true;
  copied = false;

  constructor() { }

  ngOnInit(): void { }

  generateShareLink() {
    const url = window.location.href.split('?')[0]; // Remove existing query parameters
    this.shareLink = this.includeTimestamp ? `${url}?time=${this.currentTime}` : url;
  }

  copyToClipboard() {
    navigator.clipboard.writeText(this.shareLink).then(() => {
      this.copied = true;
      setTimeout(() => (this.copied = false), 1500);
    });
  }

  toggleTimestamp() {
    this.generateShareLink(); // Regenerate link
  }

}
