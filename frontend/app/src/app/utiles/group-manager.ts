import {Cluster} from "../types/data/cluster.types";
import {Article, ArticleStatus} from "../types/data/article.types";
import {Groups} from "../types/group.types";
import {BehaviorSubject} from "rxjs";


export class GroupManager {

    $groups: BehaviorSubject<Groups>

    constructor(
        cluster: Cluster
    ) {

        const groups:Groups = {
            default: [],
            combine: [],
            ignore: [],
        }

        cluster.articles.forEach(a => {
            switch (a.status){
                case ArticleStatus.Default:
                    groups.default.push(a)
                    break
                case ArticleStatus.Combined:
                    groups.combine.push(a)
                    break
                case ArticleStatus.Ignored:
                    groups.ignore.push(a)
                    break
                default:
                    if(Object.prototype.hasOwnProperty.call(groups, a.status)){
                        groups[a.status].push(a)
                    } else {
                        groups[a.status] = [a]
                    }
            }
        })

        this.$groups = new BehaviorSubject<Groups>(groups)
    }

    getGrouping():BehaviorSubject<Groups>{
        return this.$groups
    }

    getAddableGroupingNames():BehaviorSubject<string[]>{

        const filterAddableNames = (val: string[]):string[] => {
            const nonAddableNames = ['ignore', 'combine']
            return val.filter(n => nonAddableNames.indexOf(n)<0)
        }

        const returnable = new BehaviorSubject<string[]>(filterAddableNames(Object.keys(this.$groups.value)))

        this.$groups.subscribe(v => {
            if(Object.keys(v)!==returnable.value){
                returnable.next(filterAddableNames(Object.keys(v)))
            }
        })

        return returnable

    }

    assignArticle(id:string, group:string):void {
        let article:Article|undefined = undefined

        const currentGrouping = this.$groups.value

        for(const groupName in currentGrouping){
            if(group==groupName){continue}

            const index = currentGrouping[groupName].findIndex(a => a.id===id)
            if(index>=0){
                article = currentGrouping[groupName][index]
                currentGrouping[groupName].splice(index, 1)
                break
            }
        }

        if(article){
            if(Object.prototype.hasOwnProperty.call(currentGrouping, group)){
                currentGrouping[group].push(article)
            } else {
                currentGrouping[group] = [article]
            }

            this.$groups.next(currentGrouping)
        }

        console.log(this.$groups.value)
    }

    findArticleGroup(id:string):string {

        for(const groupName in this.$groups.value){
            if(this.$groups.value[groupName].findIndex(a=>a.id===id)>=0){
                switch(groupName){
                    // case "default":
                    //     return "Sub Group 1"
                    default:
                        return groupName
                }
            }
        }

        return ArticleStatus.Default
    }

    findArticleGroupBehaviourSubject(id:string):BehaviorSubject<string>{

        const resBS = new BehaviorSubject(this.findArticleGroup(id))

        this.$groups.subscribe(_ => {
            const updatedGroup = this.findArticleGroup(id)
            console.log(updatedGroup)
            if(updatedGroup!==resBS.value){
                resBS.next(updatedGroup)
            }
        })

        return resBS

    }





}