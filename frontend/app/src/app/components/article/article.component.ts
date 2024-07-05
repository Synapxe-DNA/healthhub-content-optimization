import {Component, Input} from '@angular/core';
import {Article} from "../../types/data/article.types";
import {ArticleAttributeComponent} from "./article-attribute/article-attribute.component";
import {NgIf} from "@angular/common";
import {HashLabelComponent} from "../hash-label/hash-label.component";
import {iterator} from "rxjs/internal/symbol/iterator";
import {TuiButtonModule} from "@taiga-ui/core";
import {LucideAngularModule} from "lucide-angular";
import {JobService} from "../../services/job-builder/job.service";
import {GroupManager} from "../../utiles/group-manager";

@Component({
  selector: 'app-article',
  standalone: true,
  imports: [
    ArticleAttributeComponent,
    NgIf,
    HashLabelComponent,
    TuiButtonModule,
    LucideAngularModule
  ],
  templateUrl: './article.component.html',
  styleUrl: './article.component.css'
})
export class ArticleComponent {

  @Input() article!:Article
  
  @Input() groupManager!:GroupManager
  
  constructor(
  ) {
  }

  sortStrings(vals:string[]):string[]{
    return vals.sort((a,b)=>a.localeCompare(b))
  }

}
