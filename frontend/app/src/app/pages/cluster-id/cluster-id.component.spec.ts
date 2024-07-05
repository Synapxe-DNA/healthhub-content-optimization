import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClusterIdComponent } from './cluster-id.component';

describe('ClusterIdComponent', () => {
  let component: ClusterIdComponent;
  let fixture: ComponentFixture<ClusterIdComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClusterIdComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ClusterIdComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
