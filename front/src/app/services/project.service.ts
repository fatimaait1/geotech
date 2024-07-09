import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { TokenService } from './token.service';

export interface Project {
  name: string;
  description: string;
  East: number;
  North: number;
  geom: string;
  parameter1: number;
  parameter2: number;
  parameter3: number;
}
@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private baseUrl = 'http://127.0.0.1:8000'; 
  constructor(private http: HttpClient, private tokenservice: TokenService) { }

 getAuthHeaders(): HttpHeaders {
    const token = this.tokenservice.getToken();
    return new HttpHeaders({
      'Authorization': `${token}`
    });
  }

  getProjects(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/projects`, { headers: this.getAuthHeaders() });
  }
  
  addProject(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/projects`, data, { headers: this.getAuthHeaders() })
        .pipe(map(response => response));
}
modifyProject(name: string, newData: any): Observable<any> {
  const url = `${this.baseUrl}/projects/${name}/modify`; // Assuming you have an endpoint like /projects/:id/modify
  return this.http.put<any>(url, newData);
}


deleteProject(name: string): Observable<any> {
  return this.http.delete<any>(`${this.baseUrl}/projects/${name}`, { headers: this.getAuthHeaders() });
}

}
