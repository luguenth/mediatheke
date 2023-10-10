import { Component, Input, OnInit } from '@angular/core';
import { IVideo } from '../interfaces';
import { Router } from '@angular/router';
import { StorageService } from '../services/storage.service';

export interface ISeasonTab {
  season: ISeason;
  active: boolean;
}

export interface ISeason {
  seasonNumber: number;
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
  @Input() seriesVideos!: any[];
  @Input() video: any;
  series: ISeries = {
    seasons: [],
    name: ''
  };
  activeSeason: number | undefined;

  // Initialize the tabs with existing seasons from seriesVideos
  ngOnInit() {
    this.series.seasons = this.getSeasons();
    if (this.series.seasons.length > 0) {
      this.series.seasons[0].active = true; // Default first tab as active
    }
  }

  constructor(
    private router: Router,
    public storageService: StorageService
  ) { }

  getSeasons(): ISeasonTab[] {
    const seasons: ISeasonTab[] = [];
    this.seriesVideos.forEach((video: IVideo) => {
      // Check if season already exists
      console.log(seasons);
      const seasonIndex = seasons.findIndex(s => s.season.seasonNumber === video.season_number);
      if (seasonIndex === -1) {
        // Season does not exist, create new season
        const season: ISeason = {
          seasonNumber: video.season_number,
          episodes: [video]
        };
        seasons.push({ season, active: false });
      } else {
        // Season already exists, add episode to existing season
        seasons[seasonIndex].season.episodes.push(video);
      }

      // Set series name
      this.series.name = video.series_name;

      // Sort episodes by episode number
      seasons.forEach(s => s.season.episodes.sort((a, b) => a.episode_number - b.episode_number));

      // Sort seasons by season number
      seasons.sort((a, b) => a.season.seasonNumber - b.season.seasonNumber);

      // Set active tab if video is found
      if (video.id === this.video.id && !this.activeSeason && seasons[seasonIndex]) {
        seasons[seasonIndex].active = true;
        this.activeSeason = seasons[seasonIndex].season.seasonNumber;
      }

    }
    );
    return seasons;

  }

  navigateToEpisode(episode: IVideo) {
    this.router.navigate(['/video-detail', episode.id]);
  }

  // Sets the active tab when clicked
  selectTab(tab: ISeasonTab) {
    if (this.activeSeason) {
      this.series.seasons.forEach(s => s.active = false);
      tab.active = true;
      this.activeSeason = tab.season.seasonNumber;
    }
  }
}
