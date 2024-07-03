import { HttpClient } from "@angular/common/http";
import {Injectable, OnInit} from "@angular/core";
import {BehaviorSubject, firstValueFrom, Observable} from "rxjs";
import {environment} from "../../environments/environment";
import {Cluster} from "../../types/data/cluster.types";


@Injectable({ providedIn: "root" })
export class ClusterService implements OnInit {

  private $all_clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])
  private $clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])

  constructor(private http: HttpClient) {
  }

  ngOnInit() {
    this.loadData().catch(console.error)

    // Filtering and sorting should come into this step as well.
    this.$all_clusters.subscribe((value) => this.$clusters.next(value))
  }

  async loadData():Promise<void>{
    this.$all_clusters.next(await firstValueFrom(this.http.get<Cluster[]>(`${environment.BACKEND}/clusters`)))
  }

  getClusters(): BehaviorSubject<Cluster[]> {
    return this.$clusters
  }

  getCluster(id:string): BehaviorSubject<Cluster> {

    const getClusterWithId = (clusters:Cluster[]):Cluster => {
      const filtered = clusters.filter(c => c.id===id)
      if(filtered.length<=1){throw `Cluster with ${id} does not exist!`}
      if(filtered.length>1){throw `More than one cluster with ${id} exists!`}
      return filtered[0]
    }

    const cluster = new BehaviorSubject<Cluster>(getClusterWithId(this.$all_clusters.value))

    this.$all_clusters.subscribe(clusters => {
      const clusterOfInterest = getClusterWithId(clusters)
      if(clusterOfInterest!==cluster.value){
        cluster.next(clusterOfInterest)
      }
    })

    return cluster

  }

}
