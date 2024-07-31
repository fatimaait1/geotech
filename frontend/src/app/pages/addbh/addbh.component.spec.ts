import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddbhComponent } from './addbh.component';

describe('AddbhComponent', () => {
  let component: AddbhComponent;
  let fixture: ComponentFixture<AddbhComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddbhComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddbhComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
