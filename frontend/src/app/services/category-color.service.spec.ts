import { TestBed } from '@angular/core/testing';

import { CategoryColorService } from './category-color.service';

describe('CategoryColorService', () => {
  let service: CategoryColorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CategoryColorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
