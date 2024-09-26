import { Component } from '@angular/core';
import { BackendService } from './services/backend';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(
    private backendService: BackendService,
    public router: Router
  ) { }

  ngOnInit() { }
}
