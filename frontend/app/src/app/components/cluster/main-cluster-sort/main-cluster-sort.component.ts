import { Component } from '@angular/core';
import { TuiButtonModule, TuiDialogContext, TuiDialogService, TuiSvgModule } from '@taiga-ui/core';
import {PolymorpheusContent} from '@tinkoff/ng-polymorpheus';

import { ClusterService } from '../../../services/cluster/cluster.service';

@Component({
  selector: 'app-main-cluster-sort',
  standalone: true,
  imports: [TuiSvgModule, TuiButtonModule],
  templateUrl: './main-cluster-sort.component.html',
  styleUrl: './main-cluster-sort.component.css'
})
export class MainClusterSortComponent {

  constructor(private readonly dialogs: TuiDialogService, private clusterService:ClusterService){}

  showFilterDialog(content: PolymorpheusContent<TuiDialogContext>): void {
    this.dialogs.open(content).subscribe();
  }
}
