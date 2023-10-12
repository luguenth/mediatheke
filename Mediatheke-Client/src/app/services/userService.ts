import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, timer } from 'rxjs';
import { take } from 'rxjs/operators';
import jwt_decode from 'jwt-decode';
import { ITokenPayload, IVideo } from '../interfaces';

@Injectable({
    providedIn: 'root'
})
export class UserService {
    private _isAuthenticated = new BehaviorSubject<boolean>(false);
    private _username = new BehaviorSubject<string | null>(null);
    private _email = new BehaviorSubject<string | null>(null);
    private _role = new BehaviorSubject<string | null>(null);
    private _expirationDate = new BehaviorSubject<Date | null>(null);
    private expirationTimer: any;

    isAuthenticated$: Observable<boolean> = this._isAuthenticated.asObservable();
    username$: Observable<string | null> = this._username.asObservable();
    email$: Observable<string | null> = this._email.asObservable();
    role$: Observable<string | null> = this._role.asObservable();

    constructor() {
        this.unpackToken();
    }

    setToken(token: string) {
        localStorage.setItem('token', token);
        this.updateStateFromToken(token);
    }

    getToken(): string | null {
        return localStorage.getItem('token');
    }

    private decodeToken(token: string): ITokenPayload | null {
        try {
            return jwt_decode(token) as ITokenPayload;
        } catch {
            console.error('Failed to decode token');
            return null;
        }
    }

    private unpackToken() {
        const token = this.getToken();
        if (token) {
            this.updateStateFromToken(token);
        }
    }

    private updateStateFromToken(token: string) {
        const decoded = this.decodeToken(token);
        if (decoded) {
            this._isAuthenticated.next(this.isTokenValid(decoded));
            this._username.next(decoded.context.username);
            this._role.next(decoded.context.role);
            this._email.next(decoded.sub);
            this._expirationDate.next(new Date(decoded.exp * 1000));
            if (this.isTokenValid(decoded)) {
                this.setExpirationTimer(decoded.exp);
            }
        }
    }

    private setExpirationTimer(expirationTime: number) {
        const currentTime = Math.floor(Date.now() / 1000);
        const delay = (expirationTime - currentTime) * 1000;

        this.expirationTimer = timer(delay).pipe(take(1)).subscribe(() => {
            this.logout();
        });
    }


    private isTokenValid(decoded: ITokenPayload): boolean {
        const currentTime = Math.floor(Date.now() / 1000);  // in seconds
        return decoded.exp > currentTime;
    }

    logout() {
        localStorage.removeItem('token');
        this._isAuthenticated.next(false);
        this._username.next(null);
        this._role.next(null);
        this._email.next(null);
        this._expirationDate.next(null);
        if (this.expirationTimer) {
            this.expirationTimer.unsubscribe();
        }
    }

    get role(): string | null {
        return this._role.getValue();
    }

    get username(): string | null {
        return this._username.getValue();
    }
}
