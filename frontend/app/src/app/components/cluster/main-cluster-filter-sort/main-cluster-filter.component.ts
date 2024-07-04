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
    completed:'completed'
  }

  filterForm: FormGroup = new FormGroup({
    pending: new FormControl(true),
    completed: new FormControl(true),
  });

  constructor(private readonly dialogs: TuiDialogService, private clusterService:ClusterService){}

  showFilterDialog(content: PolymorpheusContent<TuiDialogContext>): void {
    this.dialogs.open(content).subscribe();
  } 

  filterClick() {
    this.removeAllFilters()

    let isCompleted:Boolean = this.filterForm.get(this.FILTER_NAMES.completed)?.value
    let isPending:Boolean = this.filterForm.get(this.FILTER_NAMES.pending)?.value

    if(isCompleted && isPending){
      this.clusterService.removeFilter(this.FILTER_NAMES.completed);
      this.clusterService.removeFilter(this.FILTER_NAMES.pending);
    }
    else if(isCompleted) {     // Filter Completed
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

  removeAllFilters() {
    for(let filterName in this.FILTER_NAMES) {
      this.clusterService.removeFilter(filterName);
    }
  }

  resetClick() {
    this.removeAllFilters()
    for(let filterName in this.FILTER_NAMES) {
      this.filterForm.get(filterName)?.setValue(true)
    }
  }

}
