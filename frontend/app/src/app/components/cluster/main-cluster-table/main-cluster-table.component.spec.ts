import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainClusterTableComponent } from './main-cluster-table.component';

describe('ClusterTableComponent', () => {
  let component: MainClusterTableComponent;
  let fixture: ComponentFixture<MainClusterTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainClusterTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainClusterTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
