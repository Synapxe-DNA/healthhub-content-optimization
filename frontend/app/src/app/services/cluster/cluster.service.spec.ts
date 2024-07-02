import { TestBed } from "@angular/core/testing";

import { ClusterServiceService } from "./cluster.service";

describe("ClusterServiceService", () => {
  let service: ClusterServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ClusterServiceService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
