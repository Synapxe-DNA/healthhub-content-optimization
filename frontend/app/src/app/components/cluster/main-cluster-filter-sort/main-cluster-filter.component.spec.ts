import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainClusterFilterComponent } from './main-cluster-filter.component';

describe('MainClusterFilterSortComponent', () => {
  let component: MainClusterFilterComponent;
  let fixture: ComponentFixture<MainClusterFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainClusterFilterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainClusterFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
