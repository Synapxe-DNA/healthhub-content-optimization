import { ChangeDetectionStrategy,Component, Input, ViewChild } from '@angular/core';
import { Cluster } from '../../../pages/clusters/clusters.component';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { TuiDataListWrapperModule, TuiInputNumberModule, TuiRadioBlockModule, TuiTextareaModule } from '@taiga-ui/kit';
import { TuiFormatNumberPipeModule, TuiGroupModule, TuiScrollbarModule, TuiSvgModule, tuiFormatNumber } from '@taiga-ui/core';
import { TuiComparator, TuiTableModule } from '@taiga-ui/addon-table';
import { TuiDay, TuiLetModule, TuiValidatorModule, tuiDefaultSort } from '@taiga-ui/cdk';


@Component({
  selector: 'app-main-cluster-table',
  standalone: true,
  imports: [TuiLetModule,TuiFormatNumberPipeModule,FormsModule,ReactiveFormsModule,TuiRadioBlockModule, TuiGroupModule,TuiDataListWrapperModule, TuiTableModule, TuiScrollbarModule, TuiTextareaModule, TuiInputNumberModule,TuiValidatorModule, TuiSvgModule],
  templateUrl: './main-cluster-table.component.html',
  styleUrl: './main-cluster-table.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})

export class MainClusterTableComponent {
  @Input() clusters: Cluster[] = [];
 
    readonly columns = ['articleId', 'URL', 'pillar', 'status'] as const;

    clusterSelected:FormControl = new FormControl('',Validators.required);
    
    trackByIndex(index: number): number {
        return index;
    }
 
 
}
