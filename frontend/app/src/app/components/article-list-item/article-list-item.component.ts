import {Component, Input} from '@angular/core';
import {Article} from "../../types/data/article.types";
import {GroupManager} from "../../utiles/group-manager";
import {ArticleMoreComponent} from "../article/article-more/article-more.component";

@Component({
  selector: 'app-article-list-item',
  standalone: true,
  imports: [
    ArticleMoreComponent
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

}
