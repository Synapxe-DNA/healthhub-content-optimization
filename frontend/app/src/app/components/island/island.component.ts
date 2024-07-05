import {
  AfterViewInit,
  Component,
  ContentChildren,
  ElementRef,
  Input,
  QueryList,
  TemplateRef,
  ViewChild
} from '@angular/core';
import {NgIf, NgTemplateOutlet} from "@angular/common";
import {TuiScrollbarModule} from "@taiga-ui/core";
import {TuiIslandModule} from "@taiga-ui/kit";
import {TuiOverscrollModule} from "@taiga-ui/cdk";

@Component({
  selector: 'app-island',
  standalone: true,
  imports: [
    NgTemplateOutlet,
    NgIf,
    TuiScrollbarModule,
    TuiIslandModule,
    TuiOverscrollModule
  ],
  templateUrl: './island.component.html',
  styleUrl: './island.component.css'
})
export class IslandComponent implements AfterViewInit{

  @Input() padding:boolean = true
  @Input() scroll:boolean = true

  @Input() header?: TemplateRef<any>

  @ViewChild('headerTemplate') headerTemplate!: ElementRef<HTMLDivElement>
  @ViewChild('container') container!: ElementRef<HTMLDivElement>
  @ViewChild('child') child!: ElementRef<HTMLDivElement>

  @ContentChildren('projectedContent') children?: QueryList<ElementRef>


  ngAfterViewInit(){
    if(this.children){
      const headerHeight = this.headerTemplate?this.headerTemplate.nativeElement.clientHeight:0
      this.child.nativeElement.style.height = `${this.container.nativeElement.clientHeight - (headerHeight)}px`
    }
  }


}
