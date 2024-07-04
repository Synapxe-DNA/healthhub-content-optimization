import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClusterTableComponent } from './cluster-table.component';

describe('ClusterTableComponent', () => {
  let component: ClusterTableComponent;
  let fixture: ComponentFixture<ClusterTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClusterTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ClusterTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
