import { Routes } from "@angular/router";
import { IndexComponent } from "./pages/index/index.component";
import { ClustersComponent } from "./pages/clusters/clusters.component";
import { ImprovementsComponent } from "./pages/improvements/improvements.component";
import { HarmoniseComponent } from "./pages/harmonise/harmonise.component";
import { JobsComponent } from "./pages/jobs/jobs.component";
import { TestComponent } from "./pages/test/test.component";
import {ClusterIdComponent} from "./pages/cluster-id/cluster-id.component";

export const routes: Routes = [
  {
    path: "",
    pathMatch: "full",
    redirectTo: "clusters",
  },
  {
    path: "clusters",
    children: [
      {
        path: "",
        component: ClustersComponent,
      },
      {
        path: ":id",
        component: ClusterIdComponent,
      }
    ],
  },
  {
    path: "improvements",
    children: [
      {
        path: "",
        component: ImprovementsComponent,
      },
    ],
  },
  {
    path: 'combine', children: [
      {
        path: "",
        component: HarmoniseComponent,
      },
    ],
  },
  {
    path: "jobs",
    children: [
      {
        path: "",
        component: JobsComponent,
      },
    ],
  },
  {
    path: "test",
    component: TestComponent,
  },
  {
    path: "**",
    redirectTo: "/",
  },
];
