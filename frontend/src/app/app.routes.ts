import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { NonAuthService } from './services/non-auth.service';
import { SignupComponent } from './pages/signup/signup.component';
import { HomeComponent } from './pages/home/home.component';
import { AuthGuardService } from './services/auth-guard.service';
import { MyaccountComponent } from './pages/myaccount/myaccount.component';
import { ManageusersComponent } from './pages/manageusers/manageusers.component';
import { RoleGuardService } from './services/role-guard.service';
import { BhComponent } from './pages/bh/bh.component';
import { CptComponent } from './pages/cpt/cpt.component';

export const routes: Routes = [
    { path: '', component: LoginComponent, title: 'Welcome!', canActivate: [NonAuthService]},
    { path: 'signup', component: SignupComponent, title: 'Register', canActivate: [NonAuthService]},
    { path: 'home', component: HomeComponent, title: 'Home', canActivate: [AuthGuardService]},
    { path: 'account/:username', component: MyaccountComponent, title: 'Settings'},
    { path: 'users', component: ManageusersComponent, title: 'Manage users', canActivate: [RoleGuardService]},
    { path: 'bh', component: BhComponent, title: 'Boreholes Dashboard', canActivate: [AuthGuardService]},
    { path: 'cpt', component: CptComponent, title: 'CPT Dashboard', canActivate: [AuthGuardService]},
];
