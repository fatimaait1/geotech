import { AbstractControl, FormGroup, ValidationErrors, ValidatorFn } from '@angular/forms';

export function emailDomainValidator(domainName: string): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const email = control.value as string;
    if (email && !email.endsWith(`@${domainName}`)) {
      return { emailDomainError: true };
    }
    return null;
  };
}
export const passwordMatchingValidatior: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const password = control.get('password');
  const confirmPassword = control.get('passwordretype');

  return password?.value === confirmPassword?.value ? null : { notmatched: true };
};

export function longitudeValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (value < -180 || value > 180) {
      return { longitudeInvalid: true };
    }
    return null;
  };
}

export function latitudeValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (value < -90 || value > 90) {
      return { latitudeInvalid: true };
    }
    return null;
  };
}
