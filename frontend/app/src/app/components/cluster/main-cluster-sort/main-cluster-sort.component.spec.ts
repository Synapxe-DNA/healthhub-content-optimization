import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainClusterSortComponent } from './main-cluster-sort.component';

describe('MainClusterSortComponent', () => {
  let component: MainClusterSortComponent;
  let fixture: ComponentFixture<MainClusterSortComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainClusterSortComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainClusterSortComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
