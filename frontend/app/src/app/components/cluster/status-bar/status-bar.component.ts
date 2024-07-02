import { Component } from '@angular/core';
import { TuiProgressModule } from '@taiga-ui/kit';

@Component({
  selector: 'app-status-bar',
  standalone: true,
  imports: [TuiProgressModule],
  templateUrl: './status-bar.component.html',
  styleUrl: './status-bar.component.css'
})
export class StatusBarComponent {
  value = 70

}
