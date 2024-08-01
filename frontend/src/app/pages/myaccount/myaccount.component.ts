import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-myaccount',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './myaccount.component.html',
  styleUrl: './myaccount.component.css'
})
export class MyaccountComponent {
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
