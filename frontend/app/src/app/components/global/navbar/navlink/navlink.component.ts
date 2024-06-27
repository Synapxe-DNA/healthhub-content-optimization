import { Component, Input } from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {TuiTabsModule} from "@taiga-ui/kit";

@Component({
  selector: 'app-navlink',
  standalone: true,
  imports: [
    RouterLink,
    TuiTabsModule
  ],
  templateUrl: './navlink.component.html',
  styleUrl: './navlink.component.css'
})
export class NavlinkComponent {

  @Input() to!: string

  constructor(
      private router: Router
  ) {
  }

}
