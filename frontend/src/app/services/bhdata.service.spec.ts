import { TestBed } from '@angular/core/testing';

import { BhdataService } from './bhdata.service';

describe('BhdataService', () => {
  let service: BhdataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BhdataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
