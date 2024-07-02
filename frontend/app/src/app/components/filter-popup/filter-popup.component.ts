import { Component, EventEmitter, Injectable, Input, Output, model } from "@angular/core";
import {
  FormArray,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from "@angular/forms";
import { TuiButtonModule, TuiGroupModule, TuiSvgModule } from "@taiga-ui/core";
import { TuiCheckboxBlockModule } from "@taiga-ui/kit";
import { Cluster } from "../../pages/clusters/clusters.component";
import { filter } from "d3";
import { Truck } from "lucide-angular";

@Component({
  selector: "app-filter-popup",
  standalone: true,
  imports: [
    TuiSvgModule,
    TuiButtonModule,
    TuiCheckboxBlockModule,
    FormsModule,
    ReactiveFormsModule,
    TuiGroupModule,
  ],
  templateUrl: "./filter-popup.component.html",
  styleUrl: "./filter-popup.component.css",
})
export class FilterPopupComponent {
  isFilterBtnClicked = false;
  annotationForm = new FormGroup({
    pending: new FormControl(true),
    completed: new FormControl(true),
  });

  filterForm: FormGroup = new FormGroup({});

  @Input() clusters: Cluster[] = [];
  @Output() filterSelection: EventEmitter<FormGroup> = new EventEmitter<FormGroup>;

  constructor() {
    this.filterForm = new FormGroup({
      pending: new FormControl(true),
      completed: new FormControl(true),
      clustersSelected: new FormArray([]),
    });
  }

  ngOnInit() {

    this.filterForm.valueChanges.subscribe(val=>console.log(val))


  }

  //   // annotationForm = new FormGroup({
  //   //   pending: new FormControl(true),
  //   //   completed: new FormControl(true),
  //   // });

  //   // clusterNumberForm = new FormGroup({
  //   //   clustersSelected: new FormArray([]),
  //   // });
  //   this.clusters.forEach(() =>
  //     (this.filterGroup.get("clustersSelected") as FormArray).push(
  //       new FormControl(true)
  //     )
  //   );
  // }

  ngOnChanges() {
    if (this.clusters) {
      const clustersSelected = this.filterForm.controls['clustersSelected'] as FormArray;
      this.clusters.forEach(cluster => clustersSelected.push(new FormControl(true)));
      console.log(this.clusters);
    }
  }

  filterBtnClicked() {
    this.isFilterBtnClicked = !this.isFilterBtnClicked;
    console.log("Filter button clicked: " + this.isFilterBtnClicked);
  }

  onCheckChange(target: HTMLInputElement) {
    // const selectedClusters = this.filterGroup.value.clustersSelected
    //   .map((checked:boolean, i:Number) => checked ? i : null)
    //   .filter((v:any)=> v !== null);
    //   console.log(selectedClusters)
  }

  passFilterToParent(){
    this.filterSelection.emit(this.filterForm)
  }
}
