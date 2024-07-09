import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TokenService {
  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return window.localStorage.getItem('token');
    }
    return null;
  }

  removeToken(): void {
    
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('token');
    }

  }
}
