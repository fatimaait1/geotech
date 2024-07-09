import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BhComponent } from './bh.component';

describe('BhComponent', () => {
  let component: BhComponent;
  let fixture: ComponentFixture<BhComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BhComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BhComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
