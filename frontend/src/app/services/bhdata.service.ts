import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TokenService } from './token.service';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BhdataService {
  private baseUrl = 'http://127.0.0.1:8000'; 
  constructor(private http: HttpClient, private tokenservice: TokenService) { }

 getAuthHeaders(): HttpHeaders {
    const token = this.tokenservice.getToken();
    return new HttpHeaders({
      'Authorization': `${token}`
    });
  }
  getBHs(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/bh`, { headers: this.getAuthHeaders() });
  }

  addBHS(data: any): Observable<any> {
    const headers = new HttpHeaders();
    const token = this.tokenservice.getToken();
    headers.set('Content-Type', 'multipart/form-data');
    headers.set('Authorization', `${token}`)
    return this.http.post(`${this.baseUrl}/bh`, data, { headers, reportProgress: true })
        .pipe(map(response => response));
}

getGraphs(id: number, parameter: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/bhparams/?id=${id}&parameter=${parameter}`, { headers: this.getAuthHeaders() });
}
get3D(id: number): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/bhgeol/?id=${id}`, { headers: this.getAuthHeaders() });
}
}
