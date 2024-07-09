import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { latitudeValidator, longitudeValidator, requiredValidator } from '../validators/valid';
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
projectForm = new FormGroup({
  name: new FormControl('', [Validators.required]),
  description: new FormControl('', [Validators.required]),
  parameter1: new FormControl(0, [Validators.required]),
  parameter2: new FormControl(0, [Validators.required]),
  parameter3: new FormControl(0, [Validators.required]),
  longitude: new FormControl(0, [Validators.required, longitudeValidator()]),
    latitude: new FormControl(0, [Validators.required, latitudeValidator()])
});

submitProject(): void {
  if (this.projectForm.valid) {
    const formData = this.projectForm.value;
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
    }
  )
  }
}
ngOnInit(): void  {
  if (typeof window !== undefined)
 {import('leaflet').then(L => {
  const defaultIcon = L.icon({
    iconUrl: 'assets/images/bhicon.png', // Replace with your default icon path
    iconSize: [15, 15], // Size of the icon [width, height]
iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
popupAnchor: [0, -32]
  });
      this.map = L.map('map0').setView([24.44536842957562, 54.29436681027249], 15);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(this.map);
      this.map.on('click', (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;
        this.updateMapCoordinates(lat, lng, defaultIcon);
        
        this.projectForm.patchValue({
          latitude: lat,
          longitude: lng
        });
      });

})}
}

private updateMapCoordinates(lat: number, lng: number, defaultIcon: any) {
  
      if (this.marker) {
        this.marker.setLatLng([lat, lng]);
      } else {
        this.marker = new Marker([lat, lng], { icon: defaultIcon }).addTo(this.map);
      }
      this.map.setView([lat, lng], 15);
}
}

