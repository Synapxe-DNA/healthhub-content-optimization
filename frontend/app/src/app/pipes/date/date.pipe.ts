import { Pipe, PipeTransform } from '@angular/core';
import moment from "moment";

@Pipe({
  name: 'date',
  standalone: true
})
export class DatePipe implements PipeTransform {

  transform(value: Date | moment.Moment | string, dateFormat: string="DD-MM-YYYY"): string {
    return moment(value).format(dateFormat);
  }

}
