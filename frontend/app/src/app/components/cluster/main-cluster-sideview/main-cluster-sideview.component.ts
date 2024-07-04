import { Component } from '@angular/core';
import { StatusBarComponent } from '../status-bar/status-bar.component';
import { MainClusterFilterComponent } from '../main-cluster-filter-sort/main-cluster-filter.component';
import { MainClusterSortComponent } from '../main-cluster-sort/main-cluster-sort.component';
import { TuiButtonModule, TuiDialogContext, TuiDialogService } from '@taiga-ui/core';
import {PolymorpheusContent} from '@tinkoff/ng-polymorpheus';
import { MainClusterTableComponent } from '../main-cluster-table/main-cluster-table.component';
import { ClusterService } from '../../../services/cluster/cluster.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-main-cluster-sideview',
  standalone: true,
  imports: [StatusBarComponent, MainClusterFilterComponent, MainClusterSortComponent, TuiButtonModule,MainClusterTableComponent],
  templateUrl: './main-cluster-sideview.component.html',
  styleUrl: './main-cluster-sideview.component.css'
})
export class MainClusterSideviewComponent {

  clusterSelected:String = ""

  constructor(
    private readonly dialogs: TuiDialogService, 
    private clusterSerivce: ClusterService, 
    private router:Router
  ){}

  ngOnInit() {
    this.clusterSerivce.getSelectedCluster().subscribe(res=>{ 
      this.clusterSelected=res
    })
  }

  showReviewDialog(content: PolymorpheusContent<TuiDialogContext>): void {
    this.dialogs.open(content).subscribe();
  } 

  /**
   * Method to navigate to combine page after selecting cluster
   */
  goToCombinePage(){
    this.router.navigate(['/combine']);
 }

}
