import { Component } from '@angular/core';
import { TuiButtonModule, TuiDialogContext, TuiDialogService, TuiGroupModule, TuiSvgModule } from '@taiga-ui/core';
import {PolymorpheusContent} from '@tinkoff/ng-polymorpheus';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TuiCheckboxBlockModule } from '@taiga-ui/kit';
import { ClusterService } from '../../../services/cluster/cluster.service';
import { Filter } from '../../../types/filters.types';
import { Cluster } from '../../../types/data/cluster.types';



@Component({
  selector: 'app-main-cluster-filter',
  standalone: true,
  imports: [TuiSvgModule, TuiButtonModule, FormsModule, TuiGroupModule, ReactiveFormsModule, TuiCheckboxBlockModule],
  templateUrl: './main-cluster-filter.component.html',
  styleUrl: './main-cluster-filter.component.css'
})

export class MainClusterFilterComponent {

  FILTER_NAMES = {
    pending:'pending',
    completed:'completed',
    filterCluster: 'filterCluster'
  }

  filterStatusForm: FormGroup = new FormGroup({
    pending: new FormControl(true),
    completed: new FormControl(true),
  });

  clusters: Cluster[] = []

  filterClusterForm: FormGroup = new FormGroup({});

  constructor(private readonly dialogs: TuiDialogService, private clusterService:ClusterService){
    this.clusterService.getClusters().subscribe((res:Cluster[])=>{
      if (this.clusters.length == 0){ // To keep all clusters instead of filtered clusters
        this.clusters = res
      }
      for (let cluster of res) {
        this.filterClusterForm.addControl(cluster.name, new FormControl(true))
      }
    })
  }

  showFilterDialog(content: PolymorpheusContent<TuiDialogContext>): void {
    this.dialogs.open(content).subscribe();
  }

  /**
   * Method to run all added filter
   */
  filterClick() {
    this.removeAllFilters()
    this.filterStatus()
    this.filterCluster()
  }

  /**
   * Method to add filter for the selected status
   */
  filterStatus() {
    let isCompleted:Boolean = this.filterStatusForm.get(this.FILTER_NAMES.completed)?.value
    let isPending:Boolean = this.filterStatusForm.get(this.FILTER_NAMES.pending)?.value

    if(isCompleted && isPending){
      this.clusterService.removeFilter(this.FILTER_NAMES.completed);
      this.clusterService.removeFilter(this.FILTER_NAMES.pending);
    } else if(isCompleted) {     // Filter Completed
      const completed: Filter = (clusters: Cluster[]) => {
        return clusters.filter(cluster => cluster.articles[0].status.length > 0);
      };
      this.clusterService.addFilter(this.FILTER_NAMES.completed, completed);
    } else { // Filter Pending
      const pending: Filter = (clusters: Cluster[]) => {
        return clusters.filter(cluster => cluster.articles[0].status.length == 0);
      };
      this.clusterService.addFilter(this.FILTER_NAMES.pending, pending);
    }
  }

  /**
   * Method to add filter for the selected clusters
   */
  filterCluster() {
    let clustersSelected:String[] = []
    for (let cluster of this.clusters) {
      let selectedCluster:Boolean = this.filterClusterForm.get(cluster.name)?.value
      if (selectedCluster) {
        clustersSelected.push(cluster.name)
      }
    }
    const clustersFiltered: Filter = (clusters: Cluster[]) => {
      return clusters.filter(cluster => clustersSelected.includes(cluster.name));
    };
    this.clusterService.addFilter(this.FILTER_NAMES.filterCluster, clustersFiltered);
  }

  /**
   * Method to remove all filters
   */
  removeAllFilters() {
    for(let filterStatusName in this.FILTER_NAMES) {
      this.clusterService.removeFilter(filterStatusName);
    }
  }

  /**
   * Method to remove all filters and set all checkbox state to true
   */
  resetClick() {
    this.removeAllFilters()
    for(let filterStatusName in this.FILTER_NAMES) {
      this.filterStatusForm.get(filterStatusName)?.setValue(true)
    }
    for(let cluster of this.clusters) {
      this.filterClusterForm.get(cluster.name)?.setValue(true)
    }
  }

}
