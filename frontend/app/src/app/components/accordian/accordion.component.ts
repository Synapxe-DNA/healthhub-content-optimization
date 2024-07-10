import {Component, Input} from '@angular/core';
import {TuiButtonModule} from "@taiga-ui/core";

@Component({
  selector: 'app-accordion',
  standalone: true,
  imports: [
    TuiButtonModule
  ],
  templateUrl: './accordion.component.html',
  styleUrl: './accordion.component.css'
})
export class AccordionComponent {

  /**
   * This component was created as the TUI implementation of accordion wasn't cutting it.
   */

  @Input() title!:string
  @Input() isExpand:boolean = true


  toggleExpand(){
    this.isExpand = !this.isExpand
  }


}
