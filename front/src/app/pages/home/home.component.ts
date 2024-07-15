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
map: any;
filteredProjects: Project[]= [];
searchText= '';
projectNameToModify: string = '';
role = localStorage.getItem('role');
username= '';
parameters: string[]= ['ISPT','CORE_PREC','CORE_SREC','CORE_RQD', 'Strentgh']
selectedParameter: string= 'ISPT';
selectedBH: string =''
selectedFiles: File[] = [];
Alldata: any = []
clickCounter: { [key: string]: number } = {};
data3d: any = [];
plotAll: boolean = true;
msg= '';
selectedProject=''
isclicked: boolean = false;
isclicked0: boolean = false;
tile: any
ngOnInit(): void {
  if (typeof window != 'undefined' && typeof window != 'undefined') {
    import('leaflet').then(L => {
      this.map= L.map('map');
      const customControl = L.Control.extend({
        options: {
          position: 'topright' // You can set the position of the control here
        },
        onAdd: () => {
          const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
          container.style.backgroundColor = 'white';
          container.style.width = '30px';
          container.style.height = '30px';
          container.innerHTML = '<i class="bi bi-arrow-clockwise"></i>'; // Use any icon you prefer
          container.style.textAlign = 'center';
          container.style.lineHeight = '30px';
          container.style.cursor = 'pointer';
      
          container.onclick = () => {
            this.isclicked= false
            this.isclicked0=false
            this.map.eachLayer((layer: any) => {
                this.map.removeLayer(layer);
            });
            this.getProjects(); 
          };
      
          return container;
        }
      });
      
      this.map.addControl(new customControl());
    })
    
      this.getProjects();}
}
searchProjects() {
  this.filteredProjects = this.projects.filter(project =>
    project.name.toLowerCase().includes(this.searchText.toLowerCase())
  );
}

plotGraphs2(): void {
  this.Alldata = []
  //console.log(this.clickCounter)
  Object.keys(this.clickCounter).forEach(bh => {
      this.selectedBH = bh;
      //console.log(this.selectedBH)
      this.plotGraphs();
  
  });
}
plotGraphs(): void {
  //console.log(this.selectedBH)
  if (this.selectedBH && this.clickCounter[this.selectedBH] % 2 !== 0) {
    // Adding data to the plot
    var bh= this.selectedBH;
    this.projectservice.getGraphs(this.selectedProject, this.selectedBH, this.selectedParameter).subscribe((response: any) => {
      const data = response.data;
      if (data.length === 0) {

        this.msg= 'no associated ' + this.selectedParameter + ' data to the selected borehole: ' + this.selectedBH

        alert(this.msg)
      }
      else {
      this.Alldata.push({ bh: bh, data });
      //console.log(this.Alldata)
      this.updatePlot();}
    });
  } else if (this.selectedBH && this.clickCounter[this.selectedBH] % 2 === 0) {
    // Removing data from the plot
    const index = this.Alldata.findIndex((item: { bh: string; }) => item.bh === this.selectedBH);
    if (index !== -1) {
      this.Alldata.splice(index, 1);
      this.updatePlot();
    }
  }
}

updatePlot(): void {
  const plots: Plotly.Data[] = [];
  console.log(this.Alldata)
  this.Alldata.forEach((item: { data: any; bh: string; }) => {
    const data = item.data;
    const name= item.bh;
    //console.log(name)
    const elev = data.map((row: { [x: string]: any; }) => row['elev']);
    const value = data.map((row: { [x: string]: any; }) => row['value']);

    plots.push({
      x: value,
      y: elev,
      mode: 'markers',
      marker: {size: 9},
      name: this.selectedParameter + ' - ' + name
    });

  });

  import('plotly.js-dist-min').then(Plotly => {
    Plotly.react('plot', plots, {
      xaxis: { title: this.selectedParameter, autorange: true, ticks: 'outside', tick0: 0 },
      yaxis: { title: 'Z (Elevation-Depth)', autorange: true },
      legend: {
        x: 0,
        y: -1,
        orientation: 'v',
      },
      showlegend: true,
      height: 450,
      margin: {
        l: 50, r: 50, t: 40, b: 40
      },
      title: {
        text: this.selectedParameter,
        font: {
          color: 'black'
        }
      }
    }, { responsive: true });
  });
}
zoomTo(project_name: string, x: number, y: number) {
  this.isclicked0=true
  this.map.eachLayer((layer: any) => {
    if (layer != this.tile)
                {this.map.removeLayer(layer);}
            }); 
  this.selectedProject= project_name
  this.plot3d();
  

  this.projectservice.getBHs(project_name).subscribe(response => {
    const bhs= response.data
    console.log(bhs)
    if (bhs.length == 0) {alert('No Data found in the uploaded file')}
    import('leaflet').then(L => {
      if (typeof window != undefined) {
        this.isclicked0= true;
        const defaultIcon = L.icon({
          iconUrl: 'assets/images/bhicon.png', // Replace with your default icon path
          iconSize: [32, 32], // Size of the icon [width, height]
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
  popupAnchor: [0, -32]
        });
        
        const redIcon = L.icon({
          iconUrl: 'assets/images/bhiconn2.png', // Replace with your red icon path
          iconSize: [32, 32], // Size of the icon [width, height]
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
  popupAnchor: [0, -32]
        });
        this.map.setView([y, x], 14);
        bhs.forEach((element: { [x: string]: any; }) => {
          var geojsonPoint: GeoJSON.Point = {
            type: 'Point',
            coordinates: [element['x'], element['y']]
          };

          L.geoJSON(geojsonPoint, {
            pointToLayer: (feature, latlng) => {
              return L.marker(latlng, { icon: defaultIcon });
            },
            onEachFeature: (feature, layer) => {
              layer.bindPopup(element['name']);
      layer.on('click', () => {
        //plot 2d and 3d graphs
                  this.selectedBH = element['name'];
                  this.isclicked= true;
                  if (!this.clickCounter[this.selectedBH]) {
                    this.clickCounter[this.selectedBH] = 0;
                  }
                  // Increment the counter
                  this.clickCounter[this.selectedBH] += 1;
                  //console.log(this.clickCounter[this.selectedBH]);
                  if (this.clickCounter[this.selectedBH] % 2 !== 0) {
                    (layer as L.Marker).setIcon(redIcon);
                  } else {
                    (layer as L.Marker).setIcon(defaultIcon);
                  }
                  this.plotGraphs();
                  if (!this.plotAll)
                  {this.plot3d();}
      })
  }
}).addTo(this.map); }) 

}
})
}, error => {
  console.log('invalid token', error);
  this.router.navigate(['/']);
}


)
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
    this.username= response.user;
    console.log(this.projects)
    import('leaflet').then(L => {
      if (typeof window != undefined) {
        const defaultIcon = L.icon({
          iconUrl: 'assets/images/prj3.png', // Replace with an other icon to represent project
          iconSize: [32, 32], // Size of the icon [width, height]
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
  popupAnchor: [0, -32]
        });
        
       
        this.map.setView([24.44536842957562, 54.29436681027249], 11);
        this.tile= L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        })
        this.tile.addTo(this.map);

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
              layer.bindPopup(element['name']);
              layer.on('mouseover',  (e) => {
                var popup = L.popup({offset: [0, -20]})
                    .setLatLng(e.latlng)
                    .setContent(element['name'])
                    .openOn(this.map);
            });
      layer.on('click', () => { 
        //delete x y project pointer element 
        //add a reset tool to replot projects without bhs
        this.selectedProject= element['name']
        this.map.removeLayer(layer);
        
        
        this.zoomTo(this.selectedProject, element['x'], element['y']);
      })
  }
}).addTo(this.map); }) 

}
})
}, error => {
  console.log('invalid token', error);
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

getRandomColor() {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}
plot3d(): void {
  this.projectservice.get3D(this.selectedProject).subscribe((response: any) => {
    this.data3d = response.data;
    console.log(this.data3d)
    import('plotly.js-dist-min').then(Plotly => {
      var traces: Plotly.Data[] = [];
      const colorScale: { [key: string]: string } = {
        'Silty gravelly SAND': 'rgb(255, 140, 0)',    // Dark Orange
        'Silty sandy GRAVEL': 'rgb(34, 139, 34)',     // Forest Green
        'CALCARENITE': 'gray',                       // Gray
        'SANDSTONE': 'rgb(178, 34, 34)',             // Firebrick
        'MUDSTONE': 'rgb(106, 90, 205)'              // Slate Blue
      };
      const uniqueDesc : { [key: string]: string }= {};
        if (this.plotAll) {
          // Plot all boreholes
          this.data3d.forEach((element: any) => {
            if (!colorScale[element['geol_desc']]) {
              colorScale[element['geol_desc']] = this.getRandomColor(); // Add random color for new DESC
            }
            uniqueDesc[element['geol_desc']] = colorScale[element['geol_desc']];
          traces.push({
            x: [element['x'], element['x']],
            y: [element['y'], element['y']],
            z: [element['Elev'] - element['depthFrom'], element['Elev'] - element['depthTo']],
            mode: 'lines',
            line: {
              color: colorScale[element['geol_desc']],
              width: 25,
            },
            name: element['name'],
            type: 'scatter3d',
            showlegend: false,
          });
        });
      } else {
        // Plot only selected boreholes
        const selectedBHs = Object.keys(this.clickCounter).filter(bh => this.clickCounter[bh] % 2 !== 0);
        selectedBHs.forEach(selectedBH => {
          this.data3d.filter((element: any) => element['name'] === selectedBH).forEach((element: any) => {
            traces.push({
              x: [element['x'], element['x']],
              y: [element['y'], element['y']],
              z: [element['Elev'] - element['depthFrom'], element['Elev'] - element['depthTo']],
              mode: 'lines',
              line: {
                color: colorScale[element['geol_desc']],
                width: 25,
              },
              name: element['name'],
              type: 'scatter3d',
              showlegend: false,
            });
          });
        });
      }
      Object.keys(uniqueDesc).forEach(desc => {
        traces.push({
          x: [null], // No actual points, just for the legend
          y: [null],
          z: [null],
          mode: 'lines',
          line: {
            color: colorScale[desc],
            width: 25,
          },
          name: desc,
          type: 'scatter3d',
          showlegend: true,
        });
      });
      Plotly.newPlot('3d', traces, {
        xaxis: { title: 'X-axis' },
        yaxis: { title: 'Y-axis' },
        scene: {
          aspectratio: { x: 2, y: 1, z: 1 }
        },
        margin: {
          l: 0, r: 10, b: 10, t: 20
        },
        width: 930,
        height: 500,
        showlegend: true,
      }, { responsive: true });
    });
  });
}
}