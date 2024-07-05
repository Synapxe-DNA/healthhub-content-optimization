import { Injectable } from '@angular/core';
import {Cluster} from "../../types/data/cluster.types";
import {GroupManager} from "../../utiles/group-manager";

@Injectable({
  providedIn: 'root'
})
export class JobService {

  groupManagers:{[key:string]:GroupManager} = {}

  constructor() { }

  initialise(cluster: Cluster){
    if(!this.groupManagers.hasOwnProperty(cluster.id)){
      this.groupManagers[cluster.id] = new GroupManager(cluster)
    }
  }

  getGroupManager(id:string):GroupManager{
    return this.groupManagers[id]
  }

}
