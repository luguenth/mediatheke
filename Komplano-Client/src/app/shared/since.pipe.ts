import { Pipe, PipeTransform } from '@angular/core';
import { IVideo } from '../interfaces';

@Pipe({
  name: 'since'
})
export class SincePipe implements PipeTransform {
  /*
  This Pipe takes in Date and time and gives back a human readbale estimation since when the video is available
  */

  transform(video: IVideo): string {
    const dateObj = new Date(video.date + " " + video.time);
    const now = new Date();
    const diff = now.getTime() - dateObj.getTime();
    const diffDays = Math.floor(diff / (1000 * 3600 * 24));
    const diffHours = Math.floor(diff / (1000 * 3600));
    const diffMinutes = Math.floor(diff / (1000 * 60));
    const diffSeconds = Math.floor(diff / 1000);

    if (diffDays > 365) {
      return Math.floor(diffDays / 365) + " years ago";
    } else if (diffDays > 60) {
      return Math.floor(diffDays / 60) + " months ago";
    } else if (diffDays > 14) {
      return Math.floor(diffDays / 7) + " weeks ago";
    } else if (diffDays > 0) {
      return diffDays == 1 ? diffDays + " day ago" : diffDays + " days ago";
    } else if (diffHours > 0) {
      return diffHours + " hours ago";
    } else if (diffMinutes > 0) {
      return diffMinutes + " minutes ago";
    } else if (diffSeconds > 0) {
      return diffSeconds + " seconds ago";
    } else {
      return "just now";
    }
  }

}
