import { Component } from '@angular/core';
import {GraphComponent} from "../../components/graph/graph.component";

@Component({
  selector: 'app-test',
  standalone: true,
    imports: [
        GraphComponent
    ],
  templateUrl: './test.component.html',
  styleUrl: './test.component.css'
})
export class TestComponent {

}
