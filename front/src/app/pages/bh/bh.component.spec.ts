import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BHComponent } from './bh.component';

describe('BHComponent', () => {
  let component: BHComponent;
  let fixture: ComponentFixture<BHComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BHComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BHComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
