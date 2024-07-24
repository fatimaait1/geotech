import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SignupComponent } from './pages/signup/signup.component';
import { HomeComponent } from './pages/home/home.component';
import { AuthGuard } from './services/authguard.service';
import { ManageusersComponent } from './pages/manageusers/manageusers.component';
import { RoleguardService } from './services/roleguard.service';
import { AccountComponent } from './pages/account/account.component';
import { NotAuthService } from './services/not-auth.service';

export const routes: Routes = [
    { path: '', component: LoginComponent, title: 'Welcome!', canActivate: [NotAuthService]},
    { path: 'account/:username', component: AccountComponent, title: 'Settings'},
    { path: 'users', component: ManageusersComponent, title: 'Manage users', canActivate: [RoleguardService]},
    { path: 'signup', component: SignupComponent, title: 'Register', canActivate: [NotAuthService]},
    { path: 'home', component: HomeComponent, title: 'Home', canActivate: [AuthGuard]},
    
];
