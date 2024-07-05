import { Component, Input } from '@angular/core';
import { ClusterDeprecated } from '../../../pages/clusters/clusters.component';
import { FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
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
  @Input() clusters: ClusterDeprecated[] = [];
  selectedCluster: number[] = [];

  clusterSelected:FormControl = new FormControl('',Validators.required);

  getCheckboxValues() {
    console.log("Cluster select:" + this.clusterSelected.value)
  }

  updateView(){
    console.log("updateVIew")
  }
}
