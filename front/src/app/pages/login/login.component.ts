import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { emailDomainValidator } from '../../validators/valid';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  constructor(private router: Router, private loginService: AuthService) {}
  LoginForm= new FormGroup({username: new FormControl('@nmdc-group.com', [Validators.required, Validators.email, emailDomainValidator('nmdc-group.com')]), password: new FormControl('', [Validators.required])})
  loginSubscription: Subscription | undefined;

  ngOnInit() {
    console.log(this.LoginForm.valid)
   }

  submitLogin() {
    if (this.LoginForm.valid) {
      this.loginSubscription = this.loginService.login(this.LoginForm.value).subscribe(response => {
        console.log(response)
            if (response.access_token)
            {
              this.router.navigate(['/home']);
              console.log('login success');
              console.log(response);
              localStorage.setItem('token', response.access_token);
              localStorage.setItem('role', response.role);
            }
            else {this.router.navigate(['/']);
            console.log(response.message);
            }
          },
          error => {
            console.error('Login error:', error);
            // Handle error message display (optional)
          }
        );
    }
  }
  ngOnDestroy() {
    if (this.loginSubscription) {
      this.loginSubscription.unsubscribe();
    }
  }

}

