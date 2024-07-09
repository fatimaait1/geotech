import { TestBed } from '@angular/core/testing';

import { BHService } from './bh.service';

describe('BHService', () => {
  let service: BHService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BHService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
