import { Component, Input } from "@angular/core";
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
}
