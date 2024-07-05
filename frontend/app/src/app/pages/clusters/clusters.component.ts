import {Component, OnInit} from "@angular/core";
import { FormsModule } from "@angular/forms";

import { TuiButtonModule, TuiSvgModule } from "@taiga-ui/core";

import { MainClusterTableComponent } from "../../components/cluster/main-cluster-table/main-cluster-table.component";
import { MainClusterSideviewComponent } from "../../components/cluster/main-cluster-sideview/main-cluster-sideview.component";

@Component({
  selector: "app-clusters",
  standalone: true,
  imports: [
    FormsModule,
    TuiSvgModule,
    TuiButtonModule,
    MainClusterSideviewComponent,
    MainClusterTableComponent,
  ],
  templateUrl: "./clusters.component.html",
  styleUrl: "./clusters.component.css",
})
export class ClustersComponent {}
