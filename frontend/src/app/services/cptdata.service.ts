import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TokenService } from './token.service';
import { Observable, catchError, of, shareReplay, tap } from 'rxjs';
export interface Project {
  id: number
  name: string;
  lon: number;
  lat: number;
}
@Injectable({
  providedIn: 'root'
})
export class CptdataService {

  private baseUrl = 'http://127.0.0.1:8000'; 
  private cache: Map<string, Observable<any>> = new Map();
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

  /*getGrid(id: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/grid/?id=${id}`, { headers: this.getAuthHeaders() });
  }*/

  getCPTData(id: string, type: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/cptdata/?id=${id}&type=${type}`, { headers: this.getAuthHeaders() });
  } 

  getGrid(id: number): Observable<any> {
    const cacheKey = `${id}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey) as Observable<any>;
    }

    const request$ = this.http.get<any>(`${this.baseUrl}/grid/?id=${id}`).pipe(
      tap((data: any) => console.log(`Fetched data for ${cacheKey}`, data)),
      shareReplay(1),
      catchError(error => {
        console.error(`Failed to fetch data for ${cacheKey}`, error);
        this.cache.delete(cacheKey);
        return of(null);
      })
    );

    this.cache.set(cacheKey, request$);
    return request$;
  }

  clearCache() {
    this.cache.clear();
  }

  clearCacheByKey(key: string) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
  }
}
