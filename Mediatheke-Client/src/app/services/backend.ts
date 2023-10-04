import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { IMediaItemSearchResponse, ITokenResponse, IVideo, IVideoThumbnailUrl } from '../interfaces';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { UserService } from './userService';

@Injectable({
    providedIn: 'root'
})
export class BackendService {
    // no trailing slash
    private readonly baseUrl = 'https://mediatheke.local/api';

    constructor(
        private http: HttpClient,
        private userService: UserService
    ) { }

    private get apiUrl() {
        return {
            media: `${this.baseUrl}/mediaitems`,
            auth: `${this.baseUrl}/auth`,
            thumbnail: `${this.baseUrl}/thumbnail`
        };
    }

    private getWithCredentials<T>(url: string, params?: any): Observable<T> {
        return this.http.get<T>(url, { params }).pipe(
            // If the request fails, check if the status code is 401 and if so, logout
            tap(
                _ => { },
                err => {
                    if (err.status === 401) {
                        this.userService.logout();
                    }
                }
            )
        );
    }

    private postWithCredentials<T>(url: string, body: any): Observable<T> {
        return this.http.post<T>(url, body).pipe(
            // If the request fails, check if the status code is 401 and if so, logout
            tap(
                _ => { },
                err => {
                    if (err.status === 401) {
                        this.userService.logout();
                    }
                }
            )
        );
    }

    // Media related methods
    getVideos(topic: string = ""): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/?skip=0&limit=10&random_order=true&with_thumbnail=true&longer_than=600`);
    }

    getVideo(id: string): Observable<IVideo> {
        return this.getWithCredentials<IVideo>(`${this.apiUrl.media}/${id}`);
    }

    getRecommendedVideos(id: string): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/${id}/recommended`);
    }

    getVideosByTopic(topic: string): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/topic/${topic}?skip=0&limit=100&random_order=true&with_thumbnail=false`);
    }

    searchVideos(query: string): Observable<IMediaItemSearchResponse> {
        return this.getWithCredentials<IMediaItemSearchResponse>(
            `${this.apiUrl.media}/search`,
            { query }
        );
    }

    // Auth related methods
    login(username: string, password: string): Observable<any> {

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        return this.postWithCredentials<ITokenResponse>(`${this.apiUrl.auth}/login`, formData).pipe(
            tap(data => {
                this.userService.setToken(data.access_token);
            })
        );

    }

    logout(): Observable<any> {
        return this.postWithCredentials<any>(`${this.apiUrl.auth}/logout`, {}).pipe(
            tap(_ => this.userService.logout())
        );
    }

    checkAuthStatus(): Observable<any> {
        return this.getWithCredentials<any>(`${this.apiUrl.auth}/test`);
    }

    recommend(id: number, email: string): Observable<any> {
        return this.postWithCredentials<any>(`${this.apiUrl.media}/${id}/recommend`, { email });
    }

    isRecommended(id: number, email: string): Observable<boolean> {
        return this.getWithCredentials<boolean>(`${this.apiUrl.media}/${id}/isrecommended`);
    }

    getAllRecommendations(): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/recommended?skip=0&limit=10&random_order=true`);
    }

    mightBeASeries(id: string): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/${id}/mightbeaseries`);
    }

    getSeriesFromEpisode(id: string): Observable<IVideo[]> {
        return this.getWithCredentials<IVideo[]>(`${this.apiUrl.media}/series?media_item_id=${id}`);
    }

    getThumbnail(urlItem: IVideoThumbnailUrl): Observable<IVideoThumbnailUrl> {
        // send in body
        const url = encodeURIComponent(urlItem.url);
        const mediaItemId = urlItem.media_item_id;
        return this.getWithCredentials<IVideoThumbnailUrl>(`${this.apiUrl.thumbnail}/proxy/url?media_item_id=${mediaItemId}&url=${url}`);
    }
}