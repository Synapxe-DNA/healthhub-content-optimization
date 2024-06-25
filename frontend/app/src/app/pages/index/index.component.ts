import { Component } from '@angular/core';
import {TuiButtonModule} from "@taiga-ui/core";

@Component({
  selector: 'app-index',
  standalone: true,
  imports: [
    TuiButtonModule
  ],
  templateUrl: './index.component.html',
  styleUrl: './index.component.css'
})
export class IndexComponent {

}
