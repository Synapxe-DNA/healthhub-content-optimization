import { Injectable } from '@angular/core';
import {Cluster} from "../../types/data/cluster.types";
import {GroupManager} from "../../utiles/group-manager";

@Injectable({
  providedIn: 'root'
})
export class JobService {

  groupManagers:Record<string, GroupManager> = {}

  initialise(cluster: Cluster){
    if(!Object.prototype.hasOwnProperty.call(this.groupManagers, cluster.id)){
      this.groupManagers[cluster.id] = new GroupManager(cluster)
    }
  }

  getGroupManager(id:string):GroupManager{
    return this.groupManagers[id]
  }

}
