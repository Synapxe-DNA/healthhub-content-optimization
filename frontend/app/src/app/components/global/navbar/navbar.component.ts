import { Component } from '@angular/core';
import {TuiTabsModule} from "@taiga-ui/kit";
import {LucideAngularModule} from "lucide-angular";
import {NavlinkComponent} from "./navlink/navlink.component";

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    TuiTabsModule,
    LucideAngularModule,
    NavlinkComponent
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {

}
