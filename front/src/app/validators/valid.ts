import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function emailDomainValidator(domainName: string): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const email = control.value as string;
    if (email && !email.endsWith(`@${domainName}`)) {
      return { emailDomainError: true };
    }
    return null;
  };
}


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
export function requiredValidator(control: AbstractControl): ValidationErrors | null {
  return control.value ? null : { required: true };
}