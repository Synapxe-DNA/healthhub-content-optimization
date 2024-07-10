import {AfterViewInit, Component, Input} from '@angular/core';
import {Article} from "../../types/data/article.types";
import {ArticleAttributeComponent} from "./article-attribute/article-attribute.component";
import {NgIf} from "@angular/common";
import {HashLabelComponent} from "../hash-label/hash-label.component";
import {
  TuiButtonModule,
  TuiDataListModule, TuiDropdownModule,
  TuiHostedDropdownModule, TuiSvgModule,
  TuiTextfieldControllerModule
} from "@taiga-ui/core";
import {LucideAngularModule} from "lucide-angular";
import {GroupManager} from "../../utiles/group-manager";
import {DatePipe} from "../../pipes/date/date.pipe";
import {TuiDataListDropdownManagerModule, TuiInputModule, TuiIslandModule} from "@taiga-ui/kit";
import {TuiActiveZoneModule} from "@taiga-ui/cdk";
import {FormBuilder, FormGroup, ReactiveFormsModule} from "@angular/forms";
import {ArticleMoreComponent} from "./article-more/article-more.component";

@Component({
  selector: 'app-article',
  standalone: true,
  imports: [
    ArticleAttributeComponent,
    NgIf,
    HashLabelComponent,
    TuiButtonModule,
    LucideAngularModule,
    TuiHostedDropdownModule,
    TuiDataListModule,
    DatePipe,
    TuiTextfieldControllerModule,
    TuiSvgModule,
    TuiDropdownModule,
    TuiDataListDropdownManagerModule,
    TuiActiveZoneModule,
    ReactiveFormsModule,
    TuiInputModule,
    TuiIslandModule,
    ArticleMoreComponent
  ],
  templateUrl: './article.component.html',
  styleUrl: './article.component.css'
})
export class ArticleComponent implements AfterViewInit {

  @Input() article!:Article
  @Input() groupManager!:GroupManager

  subgroup:string = "default"

  createNewSubgroupForm:FormGroup

  constructor(
      private fb: FormBuilder,
  ) {
    this.createNewSubgroupForm = this.fb.group({
      name:""
    })
  }

  ngAfterViewInit() {

    this.groupManager.findArticleGroupBehaviourSubject(this.article.id).subscribe(n => {
      this.subgroup=n
    })
  }

  sortStrings(vals:string[]):string[]{
    return vals.sort((a,b)=>a.localeCompare(b))
  }



}
