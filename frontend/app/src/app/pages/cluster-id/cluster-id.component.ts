import {ChangeDetectionStrategy, Component, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {ClusterService} from "../../services/cluster/cluster.service";
import {Cluster} from "../../types/data/cluster.types";
import {ClusterGraphComponent} from "../../components/cluster/cluster-graph/cluster-graph.component";
import {TuiInputModule, TuiIslandModule, TuiTabsModule} from "@taiga-ui/kit";
import {TuiMobileTabsModule} from "@taiga-ui/addon-mobile";
import {TuiButtonModule, TuiTextfieldControllerModule} from "@taiga-ui/core";
import {TUI_IS_ANDROID, TUI_IS_IOS} from '@taiga-ui/cdk';
import {ClusterTableComponent} from "../../components/cluster/cluster-table/cluster-table.component";
import {FormBuilder, FormGroup, ReactiveFormsModule} from "@angular/forms";
import {IslandComponent} from "../../components/island/island.component";
import {LucideAngularModule} from "lucide-angular";
import {JobService} from "../../services/job-builder/job.service";

@Component({
  selector: 'app-cluster-id',
  standalone: true,
    imports: [
        ClusterGraphComponent,
        TuiButtonModule,
        TuiTabsModule,
        TuiMobileTabsModule,
        ClusterTableComponent,
        TuiIslandModule,
        TuiInputModule,
        ReactiveFormsModule,
        TuiTextfieldControllerModule,
        IslandComponent,
        LucideAngularModule
    ],
  templateUrl: './cluster-id.component.html',
  styleUrl: './cluster-id.component.css',
  providers: [
    {
      provide: TUI_IS_IOS,
      useValue: true,
    },
    {
      provide: TUI_IS_ANDROID,
      useValue: false,
    },
  ],
})
export class ClusterIdComponent implements OnInit{

  viewTabIndex:number = 1

  private loading:boolean = true
  data:Cluster|undefined = undefined

  job:FormGroup

  constructor(
      private route: ActivatedRoute,
      private clusterService: ClusterService,
      private fb: FormBuilder,
      protected jobService: JobService,
  ) {
    this.job = this.fb.group({
      name: ""
    })
  }

  ngOnInit() {

    // Fetch data upon URL change
    this.route.paramMap.subscribe(p => {
      const id = p.get('id')
      if(!id){throw "ID not present!"}
      this.clusterService.getCluster(id).subscribe(c => {
        if(c){this.loading=false}
        this.data=c
        this.jobService.initialise(c)
      })
    })


  }



}
