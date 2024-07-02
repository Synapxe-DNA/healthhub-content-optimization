import { Component, Input } from "@angular/core";
import { TuiProgressModule } from "@taiga-ui/kit";
import { Cluster } from "../../../pages/clusters/clusters.component";
import { ClusterService } from "../../../services/cluster/cluster.service";

@Component({
  selector: "app-status-bar",
  standalone: true,
  imports: [TuiProgressModule],
  templateUrl: "./status-bar.component.html",
  styleUrl: "./status-bar.component.css",
})
export class StatusBarComponent {
  clustersCompleted = 0;
  clustersPending = 0;
  totalClusters = 0;
  statusPercentage = 0;

  constructor(private clusterService: ClusterService) {}

  ngOnInit(): void {
    this.clusterService.getCluster().subscribe((res: Cluster[]) => {
      this.calculateProgress(res);
    });
  }

  calculateProgress(res: Cluster[]) {
    for (let c of res) {
      if (c.annotationStatus == "Completed") {
        this.clustersCompleted++;
      } else {
        this.clustersPending++;
      }
    }
    this.totalClusters = this.clustersCompleted + this.clustersPending
    this.statusPercentage = (this.clustersCompleted/this.totalClusters) * 100;
  }
}
