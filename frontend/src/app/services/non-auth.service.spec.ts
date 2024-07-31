import { TestBed } from '@angular/core/testing';

import { NonAuthService } from './non-auth.service';

describe('NonAuthService', () => {
  let service: NonAuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NonAuthService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
