import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { emailDomainValidator } from '../../validators/valid';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.css'
})
export class SignupComponent {
  constructor(private router: Router, private loginService: AuthService) {}
  SignupForm= new FormGroup({username: new FormControl('@nmdc-group.com', [Validators.required, Validators.email, emailDomainValidator('nmdc-group.com')]), password: new FormControl('', [Validators.required])})
  loginSubscription: Subscription | undefined;
  ngOnInit() { }

  submitSignup() {
    if (this.SignupForm.valid) {
      //console.log(this.SignupForm.value)
      this.loginSubscription = this.loginService.signup(this.SignupForm.value).subscribe(response => {
        alert(response[0].message + '. Account verification is pending.');
        if (response[0].message == 'Account created.')  
           {
            this.router.navigate(['/']);  } // Navigate to login page after signup
           else {this.router.navigate(['/signup']);}
          },
          error => {
            console.error('Signup error:', error);
            // Handle error message display (optional)
          }
        );
    }
  }
}
