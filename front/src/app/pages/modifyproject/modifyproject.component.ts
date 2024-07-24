import { Component, EventEmitter, Inject, Output } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ProjectService } from '../../services/project.service';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-modifyproject',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './modifyproject.component.html',
  styleUrl: './modifyproject.component.css'
})
export class ModifyprojectComponent {
  projectname: string= '';
  p1: number;
  p2: number;
  p3: number;
  @Output() projectModified = new EventEmitter<void>();
  modifyprojectForm: any;
  constructor(private projectservice: ProjectService, private dialogRef: MatDialogRef<ModifyprojectComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
  this.projectname= data.projectName
  this.p1= data.parameter1,
  this.p2= data.parameter2,
  this.p3= data.parameter3
  this.modifyprojectForm = new FormGroup({
    Parameter1: new FormControl(this.p1, [Validators.required]),
    Parameter2: new FormControl(this.p2, [Validators.required]),
    Parameter3: new FormControl(this.p3, [Validators.required]),
  });
  }
 

  submitmodifyProject(): void {
    if (this.modifyprojectForm.valid) {
      const formData = this.modifyprojectForm.value;
      console.log(formData)
      this.projectservice.modifyProject(this.projectname, formData).subscribe((response) => {
        if (response[0].message == 'Project modified.') {
          console.log('project modified')
          this.projectModified.emit();
          this.dialogRef.close('success');
       }
      }, 
      (error: any) => {
        console.log(error)
      }
    )
    }
  }
}
