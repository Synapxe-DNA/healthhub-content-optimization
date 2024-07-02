import { Component, Input, ViewChild } from '@angular/core';
import { FilterPopupComponent } from '../../filter-popup/filter-popup.component';
import { TuiButtonModule, TuiSvgModule } from '@taiga-ui/core';
import { Cluster } from '../../../pages/clusters/clusters.component';

@Component({
  selector: 'app-main-cluster-filter-sort',
  standalone: true,
  imports: [FilterPopupComponent, TuiSvgModule, TuiButtonModule],
  templateUrl: './main-cluster-filter-sort.component.html',
  styleUrl: './main-cluster-filter-sort.component.css'
})
export class MainClusterFilterSortComponent {

  @ViewChild (FilterPopupComponent) filterPopup!: FilterPopupComponent;
  @Input() clusters: Cluster[] = [];

  filterBtnClick() {
    this.filterPopup.filterBtnClicked();
  }

}
