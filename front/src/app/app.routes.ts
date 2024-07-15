import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SignupComponent } from './pages/signup/signup.component';
import { HomeComponent } from './pages/home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { CptComponent } from './cpt/cpt.component';
import { BhComponent } from './bh/bh.component';
import { AuthGuard } from './services/authguard.service';
import { ManageusersComponent } from './manageusers/manageusers.component';
import { RoleguardService } from './services/roleguard.service';
import { AccountComponent } from './account/account.component';
import { NotAuthService } from './services/not-auth.service';

export const routes: Routes = [
    { path: '', component: LoginComponent, title: 'Welcome!', canActivate: [NotAuthService]},
    { path: 'account/:username', component: AccountComponent, title: 'Settings'},
    { path: 'users', component: ManageusersComponent, title: 'Manage users', canActivate: [RoleguardService]},
    { path: 'signup', component: SignupComponent, title: 'Register', canActivate: [NotAuthService]},
    { path: 'home', component: HomeComponent, title: 'Home', canActivate: [AuthGuard]},
    { path: 'project/:id', component: DashboardComponent, canActivate: [AuthGuard], children: [
        { path: '', redirectTo: 'cpt', pathMatch: 'full' },  // Default route
        { path: 'cpt', component: CptComponent },
        { path: 'bh', component: BhComponent }
      ]
    }
];
