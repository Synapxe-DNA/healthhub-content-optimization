import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArticleAttributeComponent } from './article-attribute.component';

describe('ArticleAttributeComponent', () => {
  let component: ArticleAttributeComponent;
  let fixture: ComponentFixture<ArticleAttributeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArticleAttributeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArticleAttributeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
