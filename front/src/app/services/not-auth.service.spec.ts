import { TestBed } from '@angular/core/testing';

import { NotAuthService } from './not-auth.service';

describe('NotAuthService', () => {
  let service: NotAuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NotAuthService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
