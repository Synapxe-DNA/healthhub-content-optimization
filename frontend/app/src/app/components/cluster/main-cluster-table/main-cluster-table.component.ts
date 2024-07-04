import { Component, Injectable } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { TuiDataListWrapperModule, TuiInputNumberModule, TuiRadioBlockModule, TuiTextareaModule } from '@taiga-ui/kit';
import { TuiFormatNumberPipeModule, TuiGroupModule, TuiScrollbarModule, TuiSvgModule } from '@taiga-ui/core';
import { TuiTableModule } from '@taiga-ui/addon-table';
import { TuiLetModule, TuiValidatorModule } from '@taiga-ui/cdk';
import { Cluster } from '../../../types/data/cluster.types';
import { ClusterService } from '../../../services/cluster/cluster.service';
import { Article } from '../../../types/data/article.types';
import { BehaviorSubject } from 'rxjs';


@Component({
  selector: 'app-main-cluster-table',
  standalone: true,
  imports: [TuiLetModule,TuiFormatNumberPipeModule,FormsModule,ReactiveFormsModule,TuiRadioBlockModule, TuiGroupModule,TuiDataListWrapperModule, TuiTableModule, TuiScrollbarModule, TuiTextareaModule, TuiInputNumberModule,TuiValidatorModule, TuiSvgModule],
  templateUrl: './main-cluster-table.component.html',
  styleUrl: './main-cluster-table.component.css',
})

export class MainClusterTableComponent {
  clusters:Cluster[] = [];
  selectedCluster: Number[] = [];
  readonly columns = ['id', 'title', 'description', 'author',
     'pillar', 'url' , 'status', 'labels', 'cover_image_url', 'engagement'] as const;

  clusterSelectedForm:FormControl = new FormControl('',Validators.required)

  constructor(private clusterService:ClusterService){}

  ngOnInit() {
    this.clusterService.getClusters().subscribe(
      res => {
        this.clusters = res
      }
    )
    this.clusterSelectedForm.valueChanges.subscribe(
      res=> {
        this.clusterService.updateSelectedCluster(res)
      }
    )
  }
 
}
