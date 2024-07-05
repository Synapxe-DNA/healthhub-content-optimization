import {Component, OnInit} from "@angular/core";
import { FormsModule } from "@angular/forms";

import { TuiButtonModule, TuiSvgModule } from "@taiga-ui/core";

import { MainClusterFilterSortComponent } from "../../components/cluster/main-cluster-filter-sort/main-cluster-filter-sort.component";
import { MainClusterTableComponent } from "../../components/cluster/main-cluster-table/main-cluster-table.component";
import { ClusterService } from "../../services/cluster/cluster.service";


export interface ClusterDeprecated {
  clusterId: number;
  annotationStatus: string;
  articles: ArticleDeprecated[];
}

export interface ArticleDeprecated {
  articleId: number;
  URL: string;
  pillar: string;
  status: string;
}

@Component({
  selector: "app-clusters",
  standalone: true,
  imports: [FormsModule, TuiSvgModule, TuiButtonModule, MainClusterFilterSortComponent, MainClusterTableComponent],
  templateUrl: "./clusters.component.html",
  styleUrl: "./clusters.component.css",
})
export class ClustersComponent implements OnInit {
  data: ClusterDeprecated[] = [];

  constructor(private clusterService: ClusterService) {}

  ngOnInit(): void {
    this.clusterService.getClusters().subscribe(console.log)
  }

}
