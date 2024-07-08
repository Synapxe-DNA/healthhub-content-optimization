import { Component } from '@angular/core';
import { TuiButtonModule, TuiDataListModule, TuiDialogContext, TuiDialogService, TuiDropdownModule, TuiHostedDropdownModule, TuiSvgModule } from '@taiga-ui/core';
import {PolymorpheusContent} from '@tinkoff/ng-polymorpheus';

import { ClusterService } from '../../../services/cluster/cluster.service';
import { TuiReorderModule } from '@taiga-ui/addon-table';
import { TuiComboBoxModule, TuiDataListWrapperModule, TuiSelectModule, TuiTilesModule } from '@taiga-ui/kit';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Cluster } from '../../../types/data/cluster.types';
import { Sorter } from '../../../types/sorter.types';

interface SortItem {
  index: number;
  state: boolean;
  sortMethod: (a:Cluster,b:Cluster)=> number
}

type SortItems = { [key: string]: SortItem };

@Component({
  selector: 'app-main-cluster-sort',
  standalone: true,
  imports: [TuiSvgModule, TuiButtonModule,TuiTilesModule, CommonModule],
  templateUrl: './main-cluster-sort.component.html',
  styleUrl: './main-cluster-sort.component.css'
})
export class MainClusterSortComponent {

  /**
   * 0 => same
   * -1 => a smaller than b
   * 1 => a larger than b
   */

  sortItems:SortItems = {
    "Cluster Name": {
      index:0,
      state:true,
      sortMethod:(a,b)=> {return (a.name).localeCompare(b.name)}
    },
    "Number Of Articles":{
      index:1,
      state:true,
      sortMethod:(a,b)=> {return (a.articles.length) - (b.articles.length)}
    },

  }


  numOfSorts = 2

  order = new Map();

  constructor(private readonly dialogs: TuiDialogService, private clusterService:ClusterService){}

  ngOnInit(){
    this.sortClusters() 
    for (let i = 0; i < this.numOfSorts; i++) {
      this.order.set(i,i) // The Map needs to be initialised as (Original index, Current index)
    }
  }

  showFilterDialog(content: PolymorpheusContent<TuiDialogContext>): void {
    this.dialogs.open(content).subscribe();
  }

  /**
   * Method to change the state of the sort item
   * - True represents ascending
   * - False represent descending
   * 
   */
  changeSort(item:string) {
    this.sortItems[item].state = !this.sortItems[item].state
  }

  /**
   * Method used to change the icon of the button to ascending/descending
   * 
   */
  getIcon(state:Boolean){
    if (state) {
      return 'tuiIconChevronUp'
    } else {
      return 'tuiIconChevronDown'
    }
  }

  /**
   * Method to update the sort via cluster service
   */
  sortClusters() {
    const sortOrder:string[] = []

    for (let i = 0; i < this.numOfSorts; i++) { // Used to get the sorting method order
      for (let item in this.sortItems) {
        if (this.order.get(this.sortItems[item].index) == i) {
          sortOrder.push(item)
          break
        }
      }
    }

    // Create a Sorter Anonymous function
    const sortMethodList = (a:Cluster,b:Cluster) => {
      let val = 0
      let currSortItem
      for (let i = 0; i < this.numOfSorts; i++) {
         currSortItem = this.sortItems[sortOrder[i]]
          val = currSortItem.sortMethod(a,b)
          if (val == 0) {
            continue
          } else {
            return currSortItem.state ? val : -val
          }
      }
      return val
    }

    const sorterList : Sorter = (c:Cluster[]) => {
      return c.sort(sortMethodList)
      }

    this.clusterService.updateSort(sorterList)

  }



}
