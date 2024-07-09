import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { JwtHelperService } from '@auth0/angular-jwt'

@Injectable({
  providedIn: 'root'
})
export class AuthService {
   private baseUrl = 'http://localhost:8000';  // Replace with your Flask backend URL
  private jwtHelper = new JwtHelperService();
  constructor(private http: HttpClient) { }

  signup(userData: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/signup`, userData);
  }

  login(credentials: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, credentials);
  }


  isAuthenticated(): boolean | null | "" {
    const token = localStorage.getItem('token');
    return token && !this.jwtHelper.isTokenExpired(token);
  }

}
