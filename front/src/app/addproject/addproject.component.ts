import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { latitudeValidator, longitudeValidator} from '../validators/valid';
import { ProjectService } from '../services/project.service';
import { MatDialogRef } from '@angular/material/dialog';
import { LeafletMouseEvent, Marker, latLng, tileLayer } from 'leaflet';


@Component({
  selector: 'app-addproject',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './addproject.component.html',
  styleUrl: './addproject.component.css'
})
export class AddprojectComponent {
  mapCoordinates = { lat: 0, lng: 0 };
  selectedFiles: File[] = [];
  options = {
    layers: [
      tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '...' })
    ],
    zoom: 12,
    center: latLng(38.9072, -77.0369)
  };
  private map: any;
  private marker: any;
  @Output() projectModified = new EventEmitter<void>();
constructor(private projectservice: ProjectService, private dialogRef: MatDialogRef<AddprojectComponent>) {}

onFileChange(event: any) {
  this.selectedFiles = event.target.files;
}
submitProject(): void {
  console.log(this.selectedFiles.length)
  const formData = new FormData();
  for (let i = 0; i < this.selectedFiles.length; i++) {
    formData.append('Files', this.selectedFiles[i]);
  }
    this.projectservice.addProject(formData).subscribe((response) => {
      
      console.log(response)
      if (response[0].message == 'Project created.') {
        console.log('project added')
        this.projectModified.emit();
        this.dialogRef.close('success');
     }
    }, 
    (error: any) => {
      console.log(error)
      alert(error.error.detail)
    }
  )
  
}
ngOnInit(): void  {
  
}

}

