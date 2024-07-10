import {Component, Input} from '@angular/core';
import {Article} from "../../../types/data/article.types";
import {GroupManager} from "../../../utiles/group-manager";
import {ArticleMoreComponent} from "../article-more/article-more.component";
import {TuiDropdownModule, TuiHintModule, TuiHostedDropdownModule} from "@taiga-ui/core";
import {ArticleCardComponent} from "../article-card/article-card.component";

@Component({
  selector: 'app-article-list-item',
  standalone: true,
  imports: [
    ArticleMoreComponent,
    TuiHostedDropdownModule,
    ArticleCardComponent,
    TuiDropdownModule,
    TuiHintModule
  ],
  templateUrl: './article-list-item.component.html',
  styleUrl: './article-list-item.component.css'
})
export class ArticleListItemComponent {

  /**
   * This component is to display an article component in one row.
   * Should be used in a list setting.
   */

  @Input() article!:Article
  @Input() groupManager!:GroupManager
  @Input() popoverDirection:"left"|"right" = "left"

}
