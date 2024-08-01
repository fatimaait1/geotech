import { Component } from '@angular/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { UserService, User } from '../../services/user.service';
import { ModifyuserComponent } from '../modifyuser/modifyuser.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-manageusers',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterLink, RouterOutlet],
  templateUrl: './manageusers.component.html',
  styleUrl: './manageusers.component.css'
})
export class ManageusersComponent {
  constructor(private userservice: UserService, private dialog: MatDialog, private router: Router) {}
  users: User[]= [];
  filteredUsers: User[]= [];
  searchText= '';
  username= localStorage.getItem('username');
  private dialogRef: MatDialogRef<ModifyuserComponent> | null = null;
  ngOnInit(): void {
    this.getUsers();
  }
  searchUsers() {
    this.filteredUsers = this.users.filter(user =>
      user.name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  getUsers(): void {
    this.userservice.getusers().subscribe(response => {
      this.users = response.data;
      this.filteredUsers= this.users;})
}

deleteUser(name: string): void {
  const confirmed = confirm('Are you sure you want to delete permanently this user?');
  if (confirmed) {
  this.userservice.deleteUser(name).subscribe(
    (response) => {
      console.log('user deleted');
      this.users= this.users.filter(user=> user.name !== name);
      this.filteredUsers= this.users;
      this.getUsers();
    },
    (error: any) => {
      console.log(error);
    }
  ); }
}

openModifyDialog(name: string, role: string, status: string): void {
  if (this.dialogRef) {
    this.dialogRef.close('success');
    return;
  }
  this.dialogRef = this.dialog.open(ModifyuserComponent, {
    width: '600px',
    data: {userName: name,
      role: role, 
      status: status
    }
  });
  this.dialogRef.componentInstance.userModified.subscribe(() => {
    this.getUsers();
  });
  this.dialogRef.afterClosed().subscribe(() => {
    this.dialogRef = null; // Reset the dialogRef when the dialog is closed
  });
} 

logout(): void {
  localStorage.removeItem('token');
    this.router.navigate(['/']);
}
}
