import { Component, Input } from "@angular/core";
import { TuiProgressModule } from "@taiga-ui/kit";
import { ClusterService } from "../../../services/cluster/cluster.service";
import { Cluster } from "../../../types/data/cluster.types";
import { ArticleStatus } from "../../../types/data/article.types";

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

  articlesCombined = 0;
  articlesIgnored = 0;
  articlesNotReviewed = 0;
  totalArticles = 0;

  constructor(private clusterService: ClusterService) {}

  ngOnInit(): void {
    this.clusterService.getClusters().subscribe((res: Cluster[]) => {
      this.calculateProgress(res);
    });
  }

  calculateProgress(res: Cluster[]) {
    this.calculateCompletion(res)
    this.calculateArticleStatus(res)
  }

  calculateCompletion(res: Cluster[]) {
    for (let c of res) {
      if (c.articles[0].status.length > 0) {
        this.clustersCompleted++;
      } else {
        this.clustersPending++;
      }
    }
    this.totalClusters = this.clustersCompleted + this.clustersPending
    this.statusPercentage = parseFloat(((this.clustersCompleted/this.totalClusters) * 100).toFixed(2))
  }

  calculateArticleStatus(res: Cluster[]) {
    for (let c of res) {
      this.totalArticles += c.articles.length
      for (let a of c.articles) {
        if (a.status == ArticleStatus.Combined) {
          this.articlesCombined++
        }
        if (a.status == ArticleStatus.Ignored) {
          this.articlesIgnored++
        }
      }
    }
    this.articlesNotReviewed = this.totalArticles - this.articlesCombined - this.articlesIgnored
  }
}
