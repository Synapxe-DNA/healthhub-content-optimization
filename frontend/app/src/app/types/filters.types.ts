import {Cluster} from "./data/cluster.types";


export type Filter = (arg0:Cluster[])=>Cluster[]

export type FilterGroup = Record<string, Filter>;