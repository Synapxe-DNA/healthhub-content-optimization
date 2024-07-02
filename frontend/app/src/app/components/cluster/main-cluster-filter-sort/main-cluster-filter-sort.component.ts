import { Component, Input, ViewChild } from '@angular/core';
import { FilterPopupComponent } from '../../filter-popup/filter-popup.component';
import { TuiButtonModule, TuiSvgModule } from '@taiga-ui/core';
import { Cluster } from '../../../pages/clusters/clusters.component';
import { SortPopupComponent } from '../../sort-popup/sort-popup.component';

@Component({
  selector: 'app-main-cluster-filter-sort',
  standalone: true,
  imports: [FilterPopupComponent, TuiSvgModule, TuiButtonModule, SortPopupComponent],
  templateUrl: './main-cluster-filter-sort.component.html',
  styleUrl: './main-cluster-filter-sort.component.css'
})
export class MainClusterFilterSortComponent {

  @ViewChild (FilterPopupComponent) filterPopup!: FilterPopupComponent
  @ViewChild (SortPopupComponent) sortPopup!: SortPopupComponent
  @Input() clusters: Cluster[] = [];

  filterBtnClick() {
    this.filterPopup.filterBtnClicked();
  }

  sortBtnClick() {
    this.sortPopup.sortBtnClicked();
  }
}
