import { Component, TemplateRef, ViewChild } from '@angular/core';
import { BackendService } from '../services/backend';
import { UserService } from '../services/userService';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';

@Component({
  selector: 'app-navbar-login',
  templateUrl: './navbar-login.component.html',
  styleUrls: ['./navbar-login.component.scss']
})
export class NavbarLoginComponent {
  @ViewChild('loginModal') loginModalTemplate!: TemplateRef<any>;
  modalRef?: BsModalRef;

  constructor(
    private backendService: BackendService,
    public userService: UserService,
    private modalService: BsModalService
  ) { }

  openLoginModal() {
    this.modalRef = this.modalService.show(this.loginModalTemplate, { class: 'modal-sm' });
  }

  closeModal() {
    this.modalRef?.hide();
  }

  oidcLogin() {
    window.location.href = '/api/auth/oidc/login';
  }

  onLogout() {
    this.backendService.logout().subscribe({
      next: _ => { },
      error: err => {
        console.error('Logout failed:', err);
      }
    });
  }
}
