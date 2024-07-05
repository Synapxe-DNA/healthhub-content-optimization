import {AfterViewInit, Component, ElementRef, OnInit, ViewChild, ViewRef} from '@angular/core';
import {TuiIslandModule} from "@taiga-ui/kit";
import {IslandComponent} from "../../island/island.component";
import {TuiScrollbarModule} from "@taiga-ui/core";
import {NgIf, NgTemplateOutlet} from "@angular/common";

@Component({
  selector: 'app-cluster-table',
  standalone: true,
  imports: [
    TuiIslandModule,
    IslandComponent,
    TuiScrollbarModule,
    NgIf,
    NgTemplateOutlet
  ],
  templateUrl: './cluster-table.component.html',
  styleUrl: './cluster-table.component.css'
})
export class ClusterTableComponent{



}
