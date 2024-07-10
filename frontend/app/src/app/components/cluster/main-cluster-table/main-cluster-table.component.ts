import { Component, Injectable } from "@angular/core";
import {
  FormControl,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {
  TuiDataListWrapperModule,
  TuiInputNumberModule,
  TuiRadioBlockModule,
  TuiTextareaModule,
} from "@taiga-ui/kit";

import {ScrollingModule} from '@angular/cdk/scrolling';
import {
  TuiFormatNumberPipeModule,
  TuiGroupModule,
  TuiScrollbarModule,
  TuiSvgModule,
} from "@taiga-ui/core";
import { TuiTableModule, TuiTablePaginationModule } from "@taiga-ui/addon-table";
import { TuiLetModule, TuiValidatorModule } from "@taiga-ui/cdk";
import { Cluster } from "../../../types/data/cluster.types";
import { ClusterService } from "../../../services/cluster/cluster.service";
import { HashLabelComponent } from "../../hash-label/hash-label.component";

@Component({
  selector: "app-main-cluster-table",
  standalone: true,
  imports: [
    TuiLetModule,
    TuiFormatNumberPipeModule,
    FormsModule,
    ReactiveFormsModule,
    TuiRadioBlockModule,
    TuiGroupModule,
    TuiDataListWrapperModule,
    TuiTableModule,
    TuiScrollbarModule,
    TuiTextareaModule,
    TuiInputNumberModule,
    TuiValidatorModule,
    TuiSvgModule,
    HashLabelComponent,
    ScrollingModule,
    TuiTablePaginationModule
  ],
  templateUrl: "./main-cluster-table.component.html",
  styleUrl: "./main-cluster-table.component.css",
})
export class MainClusterTableComponent {
  clusters: Cluster[] = [];
  paginatedClusters: Cluster[] = []

  page: number = 0;
  size: number = 10;
  total: number = 100

  readonly columns = [
    "id",
    "title",
    "description",
    "author",
    "pillar",
    "url",
    "status",
    "labels",
    "cover_image_url",
    "engagement",
    "views",
  ] as const;

  clusterSelectedForm: FormControl = new FormControl("", Validators.required);

  constructor(private clusterService: ClusterService) {}

  ngOnInit() {
    this.clusterService.getClusters().subscribe((res) => {
      this.clusters = res
      this.total = this.clusters.length
      this.updatePagination()
    });
  }

  sortStrings(vals:string[]):string[]{
    return vals.sort((a,b)=>a.localeCompare(b))
  }

  sortClusterSize(vals:Cluster[]):Cluster[]{
    return vals.sort((a,b)=> a.articles.length - b.articles.length)
  }

  updatePagination() {
    const startIndex = this.page * this.size;
    const endIndex = startIndex + this.size;
    this.paginatedClusters = this.clusters.slice(startIndex, endIndex);
  }

  getClusterStatus(cluster:Cluster):boolean {
    return cluster.articles[0].status.length > 0
  }
}
