import { Component, Input, OnInit } from '@angular/core';
import { IVideo } from '../interfaces';
import { Router } from '@angular/router';
import { StorageService } from '../services/storage.service';
import { MediaService } from '../services/media.service';

export interface ISeasonTab {
  season: ISeason;
  active: boolean;
}

export interface ISeason {
  season_number: number;
  episodes: IVideo[];
}

export interface ISeries {
  seasons: ISeasonTab[];
  name: string;
}

@Component({
  selector: 'app-video-series-nav',
  templateUrl: './video-series-nav.component.html',
  styleUrls: ['./video-series-nav.component.scss']
})

export class VideoSeriesNavComponent implements OnInit {
  @Input() video: any;
  activeSeason: ISeasonTab = {
    season: {
      season_number: 0,
      episodes: []
    },
    active: true
  };

  $series: ISeries = {
    seasons: [],
    name: ''
  };

  constructor(
    private mediaService: MediaService,
    private router: Router,
    public storageService: StorageService
  ) { }

  ngOnInit(): void {
    this.mediaService.getSeriesFromEpisode(this.video).subscribe(series => {
      this.$series = series;
    });
  }

  navigateToEpisode(episode: IVideo): void {
    this.router.navigate(['/video-detail', episode.id], { queryParams: { time: this.storageService.getVideoPosition(episode) } });
  }

  selectTab(season: ISeasonTab): void {
    this.$series.seasons.forEach(s => s.active = false);
    season.active = true;
  }
}
