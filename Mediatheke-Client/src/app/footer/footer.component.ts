import { Component, OnInit } from '@angular/core';
import { BackendService } from '../services/backend';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {

  public isLightTheme: boolean = true;
  public lastSync: string | null = null;

  constructor(private backendService: BackendService) { }

  ngOnInit(): void {
    this.backendService.getLastFilmlisteImport().subscribe(data => {
      if (data?.timestamp) {
        this.lastSync = new Date(data.timestamp).toLocaleString('de-DE', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    });
  }

  onThemeSwitchChange() {
    this.isLightTheme = !this.isLightTheme;

    document.body.setAttribute(
      'data-theme',
      this.isLightTheme ? 'light' : 'dark'
    );
  }

}