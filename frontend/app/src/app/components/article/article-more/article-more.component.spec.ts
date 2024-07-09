import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArticleMoreComponent } from './article-more.component';

describe('ArticleMoreComponent', () => {
  let component: ArticleMoreComponent;
  let fixture: ComponentFixture<ArticleMoreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArticleMoreComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArticleMoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
