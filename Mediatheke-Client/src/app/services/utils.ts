// url-utils.ts

import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

export function getSafeUrl(sanitizer: DomSanitizer, url: string): SafeUrl {
    return sanitizer.bypassSecurityTrustUrl(url);
}
