import { AfterViewInit, Component, ElementRef, OnInit, Renderer2, ViewChild } from '@angular/core';
import { UserService } from '../services/userService';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, AfterViewInit {
  @ViewChild('logoSvg') svgElement!: ElementRef;

  constructor(
    public userService: UserService,
    private renderer: Renderer2,
  ) { }

  ngOnInit(): void {

  }

  ngAfterViewInit() {
  }

}
