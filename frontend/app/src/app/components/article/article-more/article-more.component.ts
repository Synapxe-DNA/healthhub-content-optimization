import {AfterViewInit, Component, Input} from '@angular/core';
import {LucideAngularModule} from "lucide-angular";
import {
    TuiButtonModule,
    TuiDataListModule, TuiDropdownModule,
    TuiHostedDropdownModule,
    TuiTextfieldControllerModule
} from "@taiga-ui/core";
import {FormBuilder, FormGroup, ReactiveFormsModule} from "@angular/forms";
import {TuiDataListDropdownManagerModule, TuiInputModule} from "@taiga-ui/kit";
import {TuiActiveZoneModule} from "@taiga-ui/cdk";
import {GroupManager} from "../../../utiles/group-manager";

@Component({
  selector: 'app-article-more',
  standalone: true,
    imports: [
        LucideAngularModule,
        TuiButtonModule,
        TuiHostedDropdownModule,
        ReactiveFormsModule,
        TuiDataListDropdownManagerModule,
        TuiDataListModule,
        TuiInputModule,
        TuiTextfieldControllerModule,
        TuiActiveZoneModule,
        TuiDropdownModule
    ],
  templateUrl: './article-more.component.html',
  styleUrl: './article-more.component.css'
})
export class ArticleMoreComponent implements AfterViewInit {

    @Input() groupManager!:GroupManager
    @Input() articleId!:string

    addableGroupNames:string[] = []

    createNewSubgroupForm:FormGroup

    constructor(
        private fb: FormBuilder
    ) {
        this.createNewSubgroupForm = this.fb.group({
            name: ""
        })
    }

    ngAfterViewInit() {
        this.groupManager.getAddableGroupingNames().subscribe(v => {
            this.addableGroupNames=v
        })
    }

    assignArticle(group:string){
        if(group){
            this.groupManager.assignArticle(this.articleId, group)
        }
    }

}
