import {Article} from "./article.types";
import {Edge} from "./edge.types";

export interface Cluster {
    id: string,
    name: string,
    articles: Article[]
    edges: Edge[]
}