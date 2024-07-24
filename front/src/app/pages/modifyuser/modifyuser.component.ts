import { Component, EventEmitter, Inject, Output } from '@angular/core';
import { UserService } from '../../services/user.service';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { emailDomainValidator } from '../../validators/valid';

@Component({
  selector: 'app-modifyuser',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './modifyuser.component.html',
  styleUrl: './modifyuser.component.css'
})
export class ModifyuserComponent {
  username: string= '';
  role: string= '';
  status: string= '';
  @Output() userModified = new EventEmitter<void>();
  modifyuserForm: any;
  constructor(private userservice: UserService, private dialogRef: MatDialogRef<ModifyuserComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
  this.username= data.userName
  this.role= data.role
  this.status= data.status
  this.modifyuserForm = new FormGroup({
    username: new FormControl(this.username, [Validators.required, emailDomainValidator('nmdc-group.com')]),
    role: new FormControl(this.role, [Validators.required]),
    status: new FormControl(this.status, [Validators.required])
  });
  }
 

  submitmodifyUser(): void {
    if (this.modifyuserForm.valid) {
      const formData = this.modifyuserForm.value;
      console.log(formData)
      this.userservice.modifyUser(this.username, formData).subscribe((response) => {
        if (response[0].message == 'User modified.') {
          console.log('user modified')
          this.userModified.emit();
          this.dialogRef.close('success');
       }
      }, 
      (error: any) => {
        console.log(error)
      }
    )
    }
  }
}
