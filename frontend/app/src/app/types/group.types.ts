import {Article} from "./data/article.types";


export interface Groups {
    default: Article[],
    combine: Article[],
    ignore: Article[],
    [key:string]: Article[]
}
