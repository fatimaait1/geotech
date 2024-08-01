import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TokenService } from './token.service';
import { Observable, map } from 'rxjs';
export interface User {
  name: string;
  role: string;
  status: string
}
@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseUrl = 'http://127.0.0.1:8000'; 
  constructor(private http: HttpClient, private tokenservice: TokenService) { }
  getAuthHeaders(): HttpHeaders {
    const token = this.tokenservice.getToken();
    return new HttpHeaders({
      'Authorization': `${token}`
    });
  }

  getusers(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/users`, { headers: this.getAuthHeaders() });
  }
  
  addUser(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/users`, data, { headers: this.getAuthHeaders() })
        .pipe(map(response => response));
}
modifyUser(name: string, newData: any): Observable<any> {
  const url = `${this.baseUrl}/users/${name}/modify`; // Assuming you have an endpoint like /users/:id/modify
  return this.http.put<any>(url, newData);
}
modifyUser2(name: string, newData: any): Observable<any> {
  const url = `${this.baseUrl}/users/${name}/update`; // Assuming you have an endpoint like /users/:id/update
  return this.http.put<any>(url, newData);
}

deleteUser(name: string): Observable<any> {
  return this.http.delete<any>(`${this.baseUrl}/users/${name}`, { headers: this.getAuthHeaders() });
}
}
