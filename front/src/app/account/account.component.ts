import { Component } from '@angular/core';
import { UserService } from '../services/user.service';
import { AbstractControl, FormControl, FormGroup, ReactiveFormsModule, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
//import { matchPasswordValidator } from '../validators/valid';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
@Component({
  selector: 'app-account',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './account.component.html',
  styleUrl: './account.component.css'
})
export class AccountComponent {
  username: any;
  modifyuserForm: any;

  constructor(private userservice: UserService, private route: ActivatedRoute, private router: Router) {}
  logout(): void {
    localStorage.removeItem('token');
      this.router.navigate(['/']);
  }
  ngOnInit(): void {
    this.modifyuserForm = new FormGroup({
      password: new FormControl('',  [Validators.required]),
      passwordretype: new FormControl('', [Validators.required]),
    });
  this.username = this.route.snapshot.paramMap.get('username');
}
  submitmodifyUser(): void {
    if (this.modifyuserForm.valid) {
      const formData = { ...this.modifyuserForm.value };
      // Exclude or modify data as needed
      delete formData.passwordretype; // exclude passwordretype
      console.log(formData)
      this.userservice.modifyUser2(this.username, formData).subscribe((response) => {
        if (response[0].message == 'User modified.') {
          console.log('user modified')  
       }
      }, 
      (error: any) => {
        console.log(error)
      }
    )
    }
  }

}
