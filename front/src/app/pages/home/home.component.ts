import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { Project, ProjectService } from '../../services/project.service';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { AddprojectComponent } from '../../addproject/addproject.component';
import {MatDialog} from '@angular/material/dialog'
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ModifyprojectComponent } from '../../modifyproject/modifyproject.component';
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterLink, RouterOutlet],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  constructor(private projectservice: ProjectService,  private router: Router, private dialog: MatDialog) {}
projects: Project[]= [];
filteredProjects: Project[]= [];
searchText= '';
projectNameToModify: string = '';
role = localStorage.getItem('role');
ngOnInit(): void {
  if (typeof window != 'undefined') {
      this.getProjects();}
}
searchProjects() {
  this.filteredProjects = this.projects.filter(project =>
    project.name.toLowerCase().includes(this.searchText.toLowerCase())
  );
}
goToDetails(id: string) {
  this.router.navigate(['/project', id]);
}

addProject(): void {
  const dialogRef = this.dialog.open(AddprojectComponent, {
    width: '600px',
    
  });
  dialogRef.componentInstance.projectModified.subscribe(() => {
    this.getProjects();
  });

}
getProjects(): void {
  this.projectservice.getProjects().subscribe(response => {
    this.projects = response.data;
    this.filteredProjects= this.projects;
    console.log(this.projects)
    import('leaflet').then(L => {
      if (typeof window != undefined) {
        const defaultIcon = L.icon({
          iconUrl: 'assets/images/bhicon.png', // Replace with your default icon path
          iconSize: [32, 32], // Size of the icon [width, height]
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
  popupAnchor: [0, -32]
        });
        
       
        var map = L.map('map').setView([24.44536842957562, 54.29436681027249], 11);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        this.projects.forEach((element: { [x: string]: any; }) => {
          console.log(element['x'])
          var geojsonPoint: GeoJSON.Point = {
            type: 'Point',
            coordinates: [element['x'], element['y']]
          };

          L.geoJSON(geojsonPoint, {
            pointToLayer: (feature, latlng) => {
              return L.marker(latlng, { icon: defaultIcon });
            },
            onEachFeature: (feature, layer) => {
              const popupContent = `
            <div class=" d-flex justify-content-around">
              <h6>${element['name']}</h6>
              <button type="button" class="btn btn-info mx-1" id="details-${element['name']}">
                <i class="bi bi-bar-chart-line"></i>
              </button>
              <button type="button" class="btn btn-success mx-1" id="modify-${element['name']}">
                <i class="bi bi-sliders"></i>
              </button>
              <button type="button" class="btn btn-danger mx-1" id="delete-${element['name']}">
                <i class="bi bi-trash-fill"></i>
              </button>
            </div>
          `;
              layer.bindPopup(popupContent);
              layer.on('popupopen', () => {
                document.getElementById(`details-${element['name']}`)?.addEventListener('click', () => {
                  this.goToDetails(element['name']);
                }); 
                document.getElementById(`modify-${element['name']}`)?.addEventListener('click', () => {
                  this.openModifyDialog(element['name'], element['parameter1'], element['parameter2'], element['parameter3']);
                });
                document.getElementById(`delete-${element['name']}`)?.addEventListener('click', () => {
                  this.deleteProject(element['name']);
                });
      });
  }
}).addTo(map); }) 
}
})
}, error => {
  console.log('invalid token');
  this.router.navigate(['/']);
}


)
}

deleteProject(name: string): void {
  const confirmed = confirm('Are you sure you want to delete this project?');
  if (confirmed) {
  this.projectservice.deleteProject(name).subscribe(
    (response) => {
      console.log('Project deleted');
      this.projects = this.projects.filter(project => project.name !== name);
      this.filteredProjects= this.projects;
      this.getProjects();
    },
    (error: any) => {
      console.log(error);
    }
  ); }
}

openModifyDialog(name: string, p1: number, p2: number, p3: number): void {
  const dialogRef = this.dialog.open(ModifyprojectComponent, {
    width: '600px',
    data: {projectName: name,
      parameter1: p1, 
      parameter2: p2, 
      parameter3: p3
    }
  });
  dialogRef.componentInstance.projectModified.subscribe(() => {
    this.getProjects();
  });
}

logout(): void {
  localStorage.removeItem('token');
    this.router.navigate(['/']);
}
}