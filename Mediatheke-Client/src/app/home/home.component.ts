import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  videoRows = [
    {
      title: 'Emmpfohlen von der Community',
      description: 'Jedes Mitglied der Community kann Videos empfehlen, die dann hier angezeigt werden.',
      topic: undefined,
    },
    {
      title: 'Babylon Berlin',
      description: 'In Babylon Berlin wird die Geschichte des Kriminalkommissars Gereon Rath erzählt, der im Berlin der 1920er Jahre ermittelt.',
      topic: 'babylon berlin'
    },
  ];

  constructor() { }

  ngOnInit(): void {
  }

}
