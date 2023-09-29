import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { VideoRowComponent } from './video-row/video-row.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { VideoCardComponent } from './video-card/video-card.component';
import { DurationPipe } from './shared/duration.pipe';
import { VideoSearchComponent } from './video-search/video-search.component';
import { TypeaheadModule } from 'ngx-bootstrap/typeahead';
import { VideoDetailComponent } from './video-detail/video-detail.component';
import { TopicDetailComponent } from './topic-detail/topic-detail.component';
import { HomeComponent } from './home/home.component';
import { VideoResultGridComponent } from './video-result-grid/video-result-grid.component';
import { HeaderComponent } from './header/header.component';
import { NgxBootstrapIconsModule, allIcons } from 'ngx-bootstrap-icons';
import { FooterComponent } from './footer/footer.component';
import { NavbarLoginComponent } from './navbar-login/navbar-login.component';
import { AuthInterceptor } from './interceptors/authInterceptor';
import { VideoPlayerComponent } from './video-player/video-player.component';
import { RegisterComponent } from './register/register.component';
import { VideoSearchResultsComponent } from './video-search-results/video-search-results.component';
import { ShareComponent } from './buttons/share/share.component';
import { PopoverModule } from 'ngx-bootstrap/popover';
import { RecommendComponent } from './buttons/recommend/recommend.component';
import { ProgressbarModule } from 'ngx-bootstrap/progressbar';
import { VideoResultListComponent } from './video-result-list/video-result-list.component';
import { SincePipe } from './shared/since.pipe';

@NgModule({
  declarations: [
    AppComponent,
    VideoRowComponent,
    VideoCardComponent,
    DurationPipe,
    VideoSearchComponent,
    VideoDetailComponent,
    TopicDetailComponent,
    HomeComponent,
    VideoResultGridComponent,
    HeaderComponent,
    FooterComponent,
    NavbarLoginComponent,
    VideoPlayerComponent,
    RegisterComponent,
    VideoSearchResultsComponent,
    ShareComponent,
    RecommendComponent,
    VideoResultListComponent,
    SincePipe,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    TypeaheadModule.forRoot(),
    PopoverModule.forRoot(),
    NgxBootstrapIconsModule.pick(allIcons),
    ProgressbarModule.forRoot()
  ],
  providers: [{
    provide: HTTP_INTERCEPTORS,
    useClass: AuthInterceptor,
    multi: true
  },],
  bootstrap: [AppComponent]
})
export class AppModule { }
