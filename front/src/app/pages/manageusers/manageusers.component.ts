import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { User, UserService } from '../../services/user.service';
import { ModifyuserComponent } from '../modifyuser/modifyuser.component';
import { MatDialog } from '@angular/material/dialog';


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
  const dialogRef = this.dialog.open(ModifyuserComponent, {
    width: '600px',
    data: {userName: name,
      role: role, 
      status: status
    }
  });
  dialogRef.componentInstance.userModified.subscribe(() => {
    this.getUsers();
  });
}

logout(): void {
  localStorage.removeItem('token');
    this.router.navigate(['/']);
}
}
