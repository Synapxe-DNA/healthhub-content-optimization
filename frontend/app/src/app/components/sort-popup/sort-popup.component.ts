import { Component } from "@angular/core";
import { TuiButtonModule, TuiSvgModule } from "@taiga-ui/core";

@Component({
  selector: "app-sort-popup",
  standalone: true,
  imports: [TuiSvgModule, TuiButtonModule],
  templateUrl: "./sort-popup.component.html",
  styleUrl: "./sort-popup.component.css",
})
export class SortPopupComponent {
  isSortBtnClicked = false;

  sortBtnClicked() {
    this.isSortBtnClicked = !this.isSortBtnClicked;
    console.log("Sort button clicked: " + this.isSortBtnClicked);
  }
}
