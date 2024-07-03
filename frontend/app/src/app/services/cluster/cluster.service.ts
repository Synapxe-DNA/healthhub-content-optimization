import { HttpClient } from "@angular/common/http";
import {Injectable, OnInit} from "@angular/core";
import {BehaviorSubject, firstValueFrom, Observable} from "rxjs";
import {environment} from "../../environments/environment";
import {Cluster} from "../../types/data/cluster.types";
import {Filter, FilterGroup} from "../../types/filters.types";


@Injectable({ providedIn: "root" })
export class ClusterService implements OnInit {

  private $all_clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])
  private $clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])

  private $filters:BehaviorSubject<FilterGroup> = new BehaviorSubject<FilterGroup>({})

  constructor(
      private http: HttpClient
  ) {}

  ngOnInit() {
    this.loadData().catch(console.error)

    this.$all_clusters.subscribe(
        value => this.$clusters.next(this.applyFiltersToClusters(value, this.$filters.value))
    )
    this.$filters.subscribe(
        filters => this.$clusters.next(this.applyFiltersToClusters(this.$all_clusters.value, filters))
    )
  }

  /**
   * Method to apply filters to an array of clusters
   * @param clusters {Cluster[]}
   * @param filters {FilterGroup}
   * @return {Cluster[]}
   * @private
   */
  private applyFiltersToClusters(clusters:Cluster[], filters:FilterGroup):Cluster[] {
    let filtered = clusters
    Object.keys(filters).forEach(f => {
      filtered = filters[f](filtered)
    })
    return filtered
  }

  /**
   * Method to fetch data from the endpoint and update the local state.
   */
  async loadData():Promise<void>{
    this.$all_clusters.next(await firstValueFrom(this.http.get<Cluster[]>(`${environment.BACKEND}/clusters`)))
  }

  /**
   * Method to get a BehaviourSubject for the filtered clusters.
   * @return {Cluster[]}
   */
  getClusters(): BehaviorSubject<Cluster[]> {
    return this.$clusters
  }

  /**
   * Method to get a BehaviourSubject of a specific cluster ID.
   * @param id
   */
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

  /**
   * Method to add a filter to the data
   * @param name {string}
   * @param filter {Filter}
   */
  addFilter(name:string, filter:Filter):void {
    const filterGroup = this.$filters.value
    filterGroup[name]=filter
    this.$filters.next(filterGroup)
  }

  /**
   * Method to remove a filter by name.
   * @param name {string}
   */
  removeFilter(name:string):void {
    const filterGroup = this.$filters.value
    if(filterGroup[name]){
      delete filterGroup[name]
      this.$filters.next(filterGroup)
    }
  }



}
