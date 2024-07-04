import { Component } from '@angular/core';
import {TuiIslandModule} from "@taiga-ui/kit";

@Component({
  selector: 'app-cluster-graph',
  standalone: true,
  imports: [
    TuiIslandModule
  ],
  templateUrl: './cluster-graph.component.html',
  styleUrl: './cluster-graph.component.css'
})
export class ClusterGraphComponent {

}
