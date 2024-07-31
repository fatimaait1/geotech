import { Component, EventEmitter, Output } from '@angular/core';
import { BhdataService } from '../../services/bhdata.service';
import { MatDialogRef } from '@angular/material/dialog';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-addbh',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './addbh.component.html',
  styleUrl: './addbh.component.css'
})
export class AddbhComponent {
  @Output() bhAdded = new EventEmitter<void>();
  selectedFiles: File[] = [];
  constructor(private bhservice: BhdataService, private dialogRef: MatDialogRef<AddbhComponent>) {}

  onFileChange(event: any) {
    this.selectedFiles = event.target.files;
  }
  submitBHs(): void {
    console.log(this.selectedFiles.length)
    const formData = new FormData();
    for (let i = 0; i < this.selectedFiles.length; i++) {
      formData.append('Files', this.selectedFiles[i]);
    }
      this.bhservice.addBHS(formData).subscribe((response) => {
        
        console.log(response)
        if (response[0].message == 'BH created.') {
          console.log('BH added')
          this.bhAdded.emit();
          this.dialogRef.close('success');
       }
      }, 
      (error: any) => {
        console.log(error)
        alert(error.error.detail)
      }
    )
    
  }

  close(): void {
    this.dialogRef.close('success');
  }
}
