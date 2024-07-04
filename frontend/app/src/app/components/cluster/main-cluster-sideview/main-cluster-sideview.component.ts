import { Component } from '@angular/core';
import { StatusBarComponent } from '../status-bar/status-bar.component';
import { MainClusterFilterComponent } from '../main-cluster-filter-sort/main-cluster-filter.component';

@Component({
  selector: 'app-main-cluster-sideview',
  standalone: true,
  imports: [StatusBarComponent, MainClusterFilterComponent],
  templateUrl: './main-cluster-sideview.component.html',
  styleUrl: './main-cluster-sideview.component.css'
})
export class MainClusterSideviewComponent {

}
