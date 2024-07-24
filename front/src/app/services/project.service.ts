import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { TokenService } from './token.service';

export interface Project {
  name: string;
  project_id: string;
  x: number;
  y: number;
  date: Date;

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
    const headers = new HttpHeaders();
    const token = this.tokenservice.getToken();
    headers.set('Content-Type', 'multipart/form-data');
    headers.set('Authorization', `${token}`)
    return this.http.post(`${this.baseUrl}/projects`, data, { headers, reportProgress: true })
        .pipe(map(response => response));
}



modifyProject(name: string, newData: any): Observable<any> {
  const url = `${this.baseUrl}/projects/${name}/modify`; // Assuming you have an endpoint like /projects/:id/modify
  return this.http.put<any>(url, newData);
}


deleteProject(name: string): Observable<any> {
  return this.http.delete<any>(`${this.baseUrl}/projects/${name}`, { headers: this.getAuthHeaders() });
}

getBHs(project_name: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/data/${project_name}`, { headers: this.getAuthHeaders() });
}

get3D(project_name: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/geol/${project_name}`, { headers: this.getAuthHeaders() });
}

getGraphs(project_name: string, bhh: string, parameter: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/params/?project=${project_name}&bhh=${bhh}&parameter=${parameter}`, { headers: this.getAuthHeaders() });
}
getInterpo(project_name: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/interpo/${project_name}`, { headers: this.getAuthHeaders() });
}
}

