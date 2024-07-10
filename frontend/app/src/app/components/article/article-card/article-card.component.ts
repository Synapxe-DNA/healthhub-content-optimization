import {Component, Input, AfterViewInit} from '@angular/core';
import {GroupManager} from "../../../utiles/group-manager";
import {Article} from "../../../types/data/article.types";
import {FormBuilder, FormGroup} from "@angular/forms";
import {ArticleMoreComponent} from "../article-more/article-more.component";
import {ArticleAttributeComponent} from "../article-attribute/article-attribute.component";
import {DatePipe} from "../../../pipes/date/date.pipe";
import {HashLabelComponent} from "../../hash-label/hash-label.component";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-article-card',
  standalone: true,
  imports: [
    ArticleMoreComponent,
    ArticleAttributeComponent,
    DatePipe,
    HashLabelComponent,
    NgIf
  ],
  templateUrl: './article-card.component.html',
  styleUrl: './article-card.component.css'
})
export class ArticleCardComponent implements AfterViewInit {

  @Input() article!:Article
  @Input() groupManager!:GroupManager

  subgroup:string = "default"
  createNewSubgroupForm:FormGroup

  constructor(
    private fb:FormBuilder
  ) {
    this.createNewSubgroupForm = this.fb.group({
      name: ""
    })
  }

  ngAfterViewInit() {
    this.groupManager.findArticleGroupBehaviourSubject(this.article.id).subscribe(n=>{
      this.subgroup=n
    })
  }

  sortStrings(vals:string[]):string[]{
    return vals.sort((a,b)=>a.localeCompare(b))
  }

}
