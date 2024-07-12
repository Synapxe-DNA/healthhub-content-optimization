import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {icons, LucideAngularModule} from "lucide-angular";



@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    LucideAngularModule.pick(icons)
  ]
})
export class LucideIconImportModule { }
