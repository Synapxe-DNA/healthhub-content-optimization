import { Component, Input, ViewChild } from '@angular/core';
import { Cluster } from '../../../pages/clusters/clusters.component';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { TuiRadioBlockModule } from '@taiga-ui/kit';
import { TuiGroupModule } from '@taiga-ui/core';

@Component({
  selector: 'app-main-cluster-table',
  standalone: true,
  imports: [FormsModule,ReactiveFormsModule,TuiRadioBlockModule, TuiGroupModule],
  templateUrl: './main-cluster-table.component.html',
  styleUrl: './main-cluster-table.component.css'
})
export class MainClusterTableComponent {
  @Input() clusters: Cluster[] = [];
  selectedCluster: Number[] = [];

  clusterSelected:FormControl = new FormControl('',Validators.required);

  constructor() {
  }


  getCheckboxValues() {
    console.log("Cluster select:" + this.clusterSelected.value)
  }
  updateView(){
    
  }
}
