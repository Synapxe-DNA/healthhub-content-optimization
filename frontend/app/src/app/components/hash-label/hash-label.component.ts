import {Component, Input} from '@angular/core';
import {ColourService} from "../../services/colour/colour.service";

@Component({
  selector: 'app-hash-label',
  standalone: true,
  imports: [],
  templateUrl: './hash-label.component.html',
  styleUrl: './hash-label.component.css'
})
export class HashLabelComponent {

  @Input() text="LABEL!"
  @Input() forceColour=""

  constructor(
      protected colour: ColourService
  ) {
  }

}
