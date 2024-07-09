import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CPTComponent } from './cpt.component';

describe('CPTComponent', () => {
  let component: CPTComponent;
  let fixture: ComponentFixture<CPTComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CPTComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CPTComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
