import {HttpClient} from "@angular/common/http";
import {Injectable} from "@angular/core";
import {BehaviorSubject} from "rxjs";
import {environment} from "../../environments/environment";
import {Cluster} from "../../types/data/cluster.types";
import {Filter, FilterGroup} from "../../types/filters.types";
import axios from "axios";


@Injectable({ providedIn: "root" })
export class ClusterService {

  private $all_clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])
  private $clusters:BehaviorSubject<Cluster[]> = new BehaviorSubject<Cluster[]>([])

  private $filters:BehaviorSubject<FilterGroup> = new BehaviorSubject<FilterGroup>({})

  constructor(
      private http: HttpClient
  ) {

    this.$all_clusters.subscribe(val => {
      this.$clusters.next(val)
    })

    this.$filters.subscribe(
        filters => this.$clusters.next(this.applyFiltersToClusters(this.$all_clusters.value, filters))
    )

    this.fetchData().catch(console.error)
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
  async fetchData():Promise<void>{
    const data = await axios.get<Cluster[]>(`${environment.BACKEND}/clusters`)
    this.$all_clusters.next(data.data)
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

    const clusterOfInterest = this.$all_clusters.value.filter(c => c.id===id)[0]

    const cluster = new BehaviorSubject<Cluster>(clusterOfInterest)

    this.$all_clusters.subscribe(clusters => {
      const clusterOfInterest = clusters.filter(c=>c.id===id)[0]
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
