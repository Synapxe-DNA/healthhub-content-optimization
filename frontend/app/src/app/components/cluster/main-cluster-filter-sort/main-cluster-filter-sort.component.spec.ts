import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainClusterFilterSortComponent } from './main-cluster-filter-sort.component';

describe('MainClusterFilterSortComponent', () => {
  let component: MainClusterFilterSortComponent;
  let fixture: ComponentFixture<MainClusterFilterSortComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainClusterFilterSortComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainClusterFilterSortComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
