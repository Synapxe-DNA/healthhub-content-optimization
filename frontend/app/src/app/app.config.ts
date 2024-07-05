import {
  BrowserAnimationsModule,
  provideAnimations,
} from "@angular/platform-browser/animations";
import { TuiRootModule } from "@taiga-ui/core";
import { ApplicationConfig, importProvidersFrom } from "@angular/core";
import { provideRouter } from "@angular/router";

import { routes } from "./app.routes";
import { LucideIconImportModule } from "./modules/lucide-icon-import/lucide-icon-import.module";
import { provideHttpClient } from "@angular/common/http";
import {TuiMobileTabsModule} from "@taiga-ui/addon-mobile";

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    provideRouter(routes),
    importProvidersFrom(BrowserAnimationsModule, TuiRootModule),
    importProvidersFrom(TuiRootModule),
    importProvidersFrom(TuiMobileTabsModule),
    importProvidersFrom(LucideIconImportModule),
    provideHttpClient(),
  ],
};
