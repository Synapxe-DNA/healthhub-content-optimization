import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HarmoniseComponent } from './harmonise.component';

describe('HarmoniserComponent', () => {
  let component: HarmoniseComponent;
  let fixture: ComponentFixture<HarmoniseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HarmoniseComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HarmoniseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
