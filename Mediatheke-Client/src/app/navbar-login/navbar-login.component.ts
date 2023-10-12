import { Component } from '@angular/core';
import { BackendService } from '../services/backend';
import { UserService } from '../services/userService';

@Component({
  selector: 'app-navbar-login',
  templateUrl: './navbar-login.component.html',
  styleUrls: ['./navbar-login.component.scss']
})
export class NavbarLoginComponent {
  showLoginForm: boolean = false;
  username: string = '';
  password: string = '';
  authStatus: boolean = false;
  showErrorAnimation: boolean = false;
  tooManyLoginAttempts: boolean = false;

  constructor(private backendService: BackendService, public userService: UserService) { }

  onSubmit() {
    if (this.username && this.password) {
      this.backendService.login(this.username, this.password).subscribe({
        next: data => {
          this.showErrorAnimation = false; // reset the error animation
        },
        error: err => {
          // make case for different errors
          switch (err.status) {
            case 401:
              console.error('Login failed: Invalid username or password');
              this.showErrorAnimation = true; // show the error animation
              setTimeout(() => this.showErrorAnimation = false, 500); // reset the error animation after the animation duration
              break;
            case 429:
              console.error('Login failed: Too many login attempts');
              this.tooManyLoginAttempts = true; // show the error animation
              setTimeout(() => this.tooManyLoginAttempts = false, 60000); // reset the error animation after the animation duration
              break;
            default:
              console.error('Login failed:', err);
          }
        }
      });
    } else {
      console.error('Username and password are required');
      this.showErrorAnimation = true; // show the error animation
      setTimeout(() => this.showErrorAnimation = false, 500); // reset the error animation after the animation duration
    }
  }

  toggleLogin() {
    this.showLoginForm = !this.showLoginForm;
  }

  checkAuthStatus() {
    this.userService.isAuthenticated$.subscribe({
      next: data => {
        this.authStatus = data;
      },
      error: err => {
        console.error('Check auth status failed:', err);
      }
    });

    this.backendService.checkAuthStatus().subscribe({
      next: data => {
        this.authStatus = data.authenticated;
      },
      error: err => {
        console.error('Check auth status failed:', err);
      }
    });
  }


  onLogout() {
    this.backendService.logout().subscribe({
      next: _ => {
        this.showLoginForm = false;
      },
      error: err => {
        console.error('Logout failed:', err);
      }
    });
  }
}
