import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HashLabelComponent } from './hash-label.component';

describe('HashLabelComponent', () => {
  let component: HashLabelComponent;
  let fixture: ComponentFixture<HashLabelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HashLabelComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HashLabelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
