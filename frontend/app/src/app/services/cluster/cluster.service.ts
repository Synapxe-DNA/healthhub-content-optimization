import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { Cluster } from "../../pages/clusters/clusters.component";


@Injectable({ providedIn: "root" })
export class ClusterService {
  constructor(private http: HttpClient) {}
  
  getCluster(): Observable<Cluster[]> {
    return this.http.get<Cluster[]>("http://localhost:3000/clusters");
  }

}
