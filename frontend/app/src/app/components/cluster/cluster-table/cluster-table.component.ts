import {AfterViewInit, Component, Input} from '@angular/core';
import {TuiIslandModule} from "@taiga-ui/kit";
import {IslandComponent} from "../../island/island.component";
import {TuiButtonModule, TuiScrollbarModule} from "@taiga-ui/core";
import {NgIf, NgTemplateOutlet} from "@angular/common";
import {Cluster} from "../../../types/data/cluster.types";
import {ArticleComponent} from "../../article/article.component";
import {JobService} from "../../../services/job-builder/job.service";
import {Article} from "../../../types/data/article.types";
import {GroupManager} from "../../../utiles/group-manager";
import {ClusterService} from "../../../services/cluster/cluster.service";
import {LucideAngularModule} from "lucide-angular";

@Component({
  selector: 'app-cluster-table',
  standalone: true,
  imports: [
    TuiIslandModule,
    IslandComponent,
    TuiScrollbarModule,
    NgIf,
    NgTemplateOutlet,
    ArticleComponent,
    LucideAngularModule,
    TuiButtonModule
  ],
  templateUrl: './cluster-table.component.html',
  styleUrl: './cluster-table.component.css'
})
export class ClusterTableComponent implements AfterViewInit{

  @Input() cluster!:Cluster|undefined

  groupManager:GroupManager|undefined
  articles:Article[] = []

  constructor(
      protected jobService:JobService,
      private clusterService:ClusterService
  ) {
  }

  ngAfterViewInit(){
    if(this.cluster){
      this.clusterService.getCluster(this.cluster?.id || "").subscribe(a => {this.articles = a.articles})
    }
  }


}
