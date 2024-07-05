import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-article-attribute',
  standalone: true,
  imports: [],
  templateUrl: './article-attribute.component.html',
  styleUrl: './article-attribute.component.css'
})
export class ArticleAttributeComponent {

  @Input() title:string = "ATTR!"

}
