import { Component } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
})
export class LoginPage  {
  username: string = '';
  password: string = '';
  passwordType: string = 'password';
  passwordIcon: string = 'eye-off-outline';
  constructor(private apiService: ApiService, private router: Router) {}



  ionViewWillEnter() {
    console.log('Entrando a la vista Login.');
    // Aquí puedes inicializar cualquier dato necesario o realizar acciones adicionales
    this.username = '';
    this.password = '';
  }


  async login() {
    const success = await this.apiService.login(this.username, this.password);
    if (success) {
      console.log('Login exitoso');
      this.router.navigate(['/home']);
    }
  }

  togglePasswordVisibility() {
    if (this.passwordType === 'password') {
      this.passwordType = 'text';
      this.passwordIcon = 'eye-outline';
    } else {
      this.passwordType = 'password';
      this.passwordIcon = 'eye-off-outline';
    }
  }

  clearCredentials() {
    this.username = '';
    this.password = '';
  }
}
