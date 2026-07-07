import { LOCALE_ID, enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

// Video.js v10 - register custom elements
import '@videojs/html/video/player';
import '@videojs/html/video/skin';

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic()
  .bootstrapModule(AppModule, {
    providers: [{ provide: LOCALE_ID, useValue: 'de' }],
  })
  .catch((err) => console.error(err));
