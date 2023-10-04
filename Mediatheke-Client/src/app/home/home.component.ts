import { Component, OnInit } from '@angular/core';
import { home_topics } from '../topics';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  videoRows = home_topics;

  constructor() { }

  ngOnInit(): void {
  }

}
