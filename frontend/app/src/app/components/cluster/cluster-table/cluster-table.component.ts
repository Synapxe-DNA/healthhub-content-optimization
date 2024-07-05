import { Component, Input} from '@angular/core';
import {TuiIslandModule} from "@taiga-ui/kit";
import {IslandComponent} from "../../island/island.component";
import {TuiScrollbarModule} from "@taiga-ui/core";
import {NgIf, NgTemplateOutlet} from "@angular/common";
import {Cluster} from "../../../types/data/cluster.types";
import {ArticleComponent} from "../../article/article.component";
import {JobService} from "../../../services/job-builder/job.service";

@Component({
  selector: 'app-cluster-table',
  standalone: true,
  imports: [
    TuiIslandModule,
    IslandComponent,
    TuiScrollbarModule,
    NgIf,
    NgTemplateOutlet,
    ArticleComponent
  ],
  templateUrl: './cluster-table.component.html',
  styleUrl: './cluster-table.component.css'
})
export class ClusterTableComponent{

  @Input() cluster!:Cluster|undefined

  constructor(
      protected jobService:JobService
  ) {
  }


}
