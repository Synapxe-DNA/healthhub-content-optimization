import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainClusterSideviewComponent } from './main-cluster-sideview.component';

describe('MainClusterSideviewComponent', () => {
  let component: MainClusterSideviewComponent;
  let fixture: ComponentFixture<MainClusterSideviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainClusterSideviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainClusterSideviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
