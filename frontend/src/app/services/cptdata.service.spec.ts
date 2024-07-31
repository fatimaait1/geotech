import { TestBed } from '@angular/core/testing';

import { CptdataService } from './cptdata.service';

describe('CptdataService', () => {
  let service: CptdataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CptdataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
