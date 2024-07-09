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

    /**
      * Retrieves a BehaviorSubject containing the names of groups that can have articles added to them,
      * excluding specific non-addable group names.
      * @returns BehaviorSubject<string[]> A BehaviorSubject emitting an array of addable group names.
      */
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

    /**
      * Assigns an article to a specified group and removes it from its current group.
      * @param id The ID of the article to be assigned.
      * @param group The name of the group to which the article will be assigned.
      */
    assignArticle(id:string, group:string):void {
        // Initialize an undefined variable to hold the article if found
        let article:Article|undefined = undefined

        // Get the current state of article groupings
        const currentGrouping = this.$groups.value

        // Iterate over each group to find and remove the article from its current group
        for(const groupName in currentGrouping){
            if(group==groupName){continue} // Skip the target group to avoid unnecessary checks

            const index = currentGrouping[groupName].findIndex(a => a.id===id) // Find the index of the article in the current group
            if(index>=0){
                article = currentGrouping[groupName][index] // Store the article
                currentGrouping[groupName].splice(index, 1) // Remove the article from its current group
                break // Exit the loop as the article is found and removed
            }
        }

        // If the article was found and removed, add it to the target group
        if(article){
            if(Object.prototype.hasOwnProperty.call(currentGrouping, group)){
                currentGrouping[group].push(article) // Add to existing group
            } else {
                currentGrouping[group] = [article] // Create new group with the article
            }

            // Update the groups BehaviorSubject with the new state
            this.$groups.next(currentGrouping)
        }
    }

    /**
      * Finds the name of the group that contains the article with the specified ID.
      * @param id The ID of the article to find.
      * @returns The name of the group containing the article, or a default status if not found.
      */
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

    /**
    * Retrieves a BehaviorSubject that emits the current article group and updates when the group changes.
    * @param id The ID of the article group to find.
    * @returns BehaviorSubject emitting the current article group.
    */
    findArticleGroupBehaviourSubject(id:string):BehaviorSubject<string>{
        // Create a BehaviorSubject to emit the current article group found by ID
        const resBS = new BehaviorSubject(this.findArticleGroup(id))

        // Subscribe to the $groups observable to update the BehaviorSubject value
        // whenever the groups data changes
        this.$groups.subscribe(_ => {
            const updatedGroup = this.findArticleGroup(id)
            // Check if the updated group is different from the current BehaviorSubject value
            if(updatedGroup !== resBS.value){
                // Emit the new group value through the BehaviorSubject
                resBS.next(updatedGroup)
            }
        })

        // Return the BehaviorSubject allowing subscribers to receive updates
        return resBS

    }





}