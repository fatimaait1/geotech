
import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { Box, CptdataService, Project } from '../../services/cptdata.service';
import * as L from 'leaflet';
import Plotly, { Data } from 'plotly.js-dist-min';
interface FlattenedCptInfo {
  box_name: string;
  subcontractor: string;
  sample_date: string; // Change Date to string for easier formatting
  type: string;
}
@Component({
  selector: 'app-cpt',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterLink, RouterOutlet],
  templateUrl: './cpt.component.html',
  styleUrl: './cpt.component.css'
})

export class CptComponent {
  constructor(private router: Router, private cptdata: CptdataService) {}
  map: any;
  tile: any;
  role = localStorage.getItem('role');
  username= localStorage.getItem('username');
  projects: Project[]= [];
filteredProjects: Project[]= [];
searchText= '';
cpttype= '';
cptname= '';
selectedProject: number = 0
selectedBox='';
isclicked: boolean= false;
selectedType= 'PRE'
types= ['PRE', 'POST', 'PRE and POST']
isloading=false
cptData: any;
boxes: Box[]=[]
//flattenedData: FlattenedCptInfo[] = [];
startDate: string = '';
endDate: string = '';
filteredData: Box[] = [];
totalPre= 0
totalPost=0
selectedprojectname=''
ngOnInit(): void {
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
             this.selectedProject=0
             this.map.eachLayer((layer: any) => {
                 this.map.removeLayer(layer);
             });
             this.getProjects(); 
           };
       
           return container;
         }
       });
       
       this.map.addControl(new customControl());

     
     this.getProjects();
   
 }

searchProjects() {
  this.filteredProjects = this.projects.filter(project =>
    project.name.toLowerCase().includes(this.searchText.toLowerCase())
  );
}

searchName() {
  this.filteredData = this.boxes.filter(cpt =>
    cpt.box_name.toLowerCase().includes(this.cptname.toLowerCase())
  );
  this.calculateTotals();
}

searchType() {
  this.filteredData = this.boxes.filter(cpt =>
    cpt.cpt_info.type.toLowerCase().includes(this.cpttype.toLowerCase())
  );
  this.calculateTotals();
}
getProjects(): void {
  this.cptdata.getProjects().subscribe(response => {
    this.projects = response.data;
    this.filteredProjects= this.projects;
    //console.log(this.projects)

     
        const defaultIcon = L.icon({
          iconUrl: 'assets/img/prj3.png', // Replace with an other icon to represent project
          iconSize: [32, 32], // Size of the icon [width, height]
  iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
  popupAnchor: [0, -32]
        });
        
       
        this.map.setView([24.48985336558, 54.4207], 10);
        this.tile= L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        })
        this.tile.addTo(this.map);

        this.projects.forEach((element: { [x: string]: any; }) => {
          var geojsonPoint: GeoJSON.Point = {
            type: 'Point',
            coordinates: [element['lon'], element['lat']]
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
        this.selectedProject= +element['id']
        this.selectedprojectname=element['name']
        this.zoomTo(this.selectedProject, element['lon'], element['lat']);
      })
  }
}).addTo(this.map); }) 



}, error => {
  console.log('invalid token', error);
  this.router.navigate(['/']);
}


)
}
/*flattenData(boxes: Box[]): void {
  this.flattenedData = boxes.reduce((acc, box) => {
    const cptRows = box.cpt_info.map(cpt => ({
      box_name: box.box_name,
      subcontractor: cpt.subcontractor,
      sample_date: new Date(cpt.sample_date).toLocaleDateString(), // Format the date as a string
      type: cpt.type
    }));
    return acc.concat(cptRows);
  }, [] as FlattenedCptInfo[]);
}


if you want this to not concat rows with same box_name, sample_date and type: 
flattenData(boxes: Box[]): void {
  const uniqueEntries = new Set<string>();

  this.flattenedData = boxes.reduce((acc, box) => {
    const cptRows = box.cpt_info.map(cpt => {
      const entryKey = `${box.box_name}-${new Date(cpt.sample_date).toLocaleDateString()}-${cpt.type}`;
      if (!uniqueEntries.has(entryKey)) {
        uniqueEntries.add(entryKey);
        return {
          box_name: box.box_name,
          subcontractor: cpt.subcontractor,
          sample_date: new Date(cpt.sample_date).toLocaleDateString(), // Format the date as a string
          type: cpt.type
        };
      }
      return null;
    }).filter(row => row !== null); // Filter out null entries

    return acc.concat(cptRows);
  }, [] as FlattenedCptInfo[]);
}*/
applyDateFilter(): void {
  const start = this.startDate ? new Date(this.startDate) : new Date('1970-01-01');
  const end = this.endDate ? new Date(this.endDate) : new Date();

  this.filteredData = this.boxes.filter(cpt => {
    const sampleDate = new Date(cpt.cpt_info.sample_date);
    return sampleDate >= start && sampleDate <= end;
  });
  this.calculateTotals();
}
zoomTo(project_id: number, lng: number, lat: number): void {
  this.isloading= true
  //console.log(lat, lng)
  this.selectedProject=project_id

this.cptdata.getGrid(project_id).subscribe(response => {
  //console.log(response.data)
  this.boxes= response.data
  //this.flattenData(this.boxes);
  this.filteredData = [...this.boxes];
  this.calculateTotals();
  if (this.boxes.length == 0) {alert('There is no box with CPT data in this project.')
    this.isloading= false
    this.selectedProject=0
  }
  else {this.map.eachLayer((layer: any) => {
    if (layer != this.tile)
                {this.map.removeLayer(layer);}
            });
  this.map.setView([lat, lng], 14);
  this.boxes.forEach((element: { [x: string]: any; }) => {
    const geoJsonLayer = L.geoJSON(element['geom'], {
      onEachFeature: (feature, layer) => {
        layer.bindPopup(element['box_name']);
        layer.on('click', () => {
          
            //this.selectedBox= +element['id'];
            this.selectedBox= element['box_name']
            this.plot(project_id, this.selectedBox, this.selectedType)
        })
      }
    });
    geoJsonLayer.addTo(this.map);
    this.map.fitBounds(geoJsonLayer.getBounds());
    this.isloading= false
  })
}
})
}
calculateTotals(): void {
  this.totalPre = this.filteredData.filter(cpt => cpt.cpt_info.type === 'PRE').length;
  this.totalPost = this.filteredData.filter(cpt => cpt.cpt_info.type === 'POST' || cpt.cpt_info.type === 'PO').length;
}
getRandomColor() {
  const getRandomValue = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

  // Adjust the RGB ranges to focus on blue nuances
  const r = getRandomValue(0, 255);   // Red: 0-50 (minimal influence)
  const g = getRandomValue(0, 255);   // Green: 0-50 (minimal influence)
  const b = getRandomValue(200, 255); // Blue: 200-255 (dominant blue)

  // Convert RGB values to hex
  const toHex = (value: number) => value.toString(16).padStart(2, '0').toUpperCase();
  console.log(`#${toHex(r)}${toHex(g)}${toHex(b)}`)
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

plot(prjid: number, id: string, type: string): void {
  this.isclicked = true
  this.selectedBox= id
  this.selectedType= type
  this.cptdata.getCPTData(prjid, id, type).subscribe(response => {
    const data = response.cpt_data;
    this.cptData= data
    console.log(this.cptData)
    // Initialize data arrays
    const fsData: Partial<Plotly.Data>[] = [];
    const qcData: Partial<Plotly.Data>[] = [];
    
    let hasMeasurements = false;

    data.forEach((cpt: { measurements: any[]; box_name: any; type: any; }) => {
      const depth: number[] = [];
      const fs: number[] = [];
      const qc: number[] = [];

      if (cpt.measurements.length > 0) {
        hasMeasurements = true;

        cpt.measurements.forEach((meas: { depth: number; fs: number; qc: number; }) => {
          depth.push(meas.depth);
          fs.push(meas.fs);
          qc.push(meas.qc);
        });

        // Add fs data to plot
        fsData.push({
          x: fs,
          y: depth,
          type: 'scatter',
          mode: 'lines',
          line: {
            color: this.getRandomColor(), // Ensure this generates a new color each time
            width: 2,
          },
          name: `${cpt.type} CPT: ${cpt.box_name}`
        });

        // Add qc data to plot
        qcData.push({
          x: qc,
          y: depth,
          type: 'scatter',
          mode: 'lines',
          line: {
            color: this.getRandomColor(), // Ensure this generates a new color each time
            width: 2,
          },
          name: `${cpt.type} CPT: ${cpt.box_name}`
        });
      }
    });

    if (!hasMeasurements) {
      alert('There is no ' + this.selectedType + ' CPT Data for the selected Box.');
    }

    // Plot fs data
    Plotly.newPlot('fs', fsData, {
      xaxis: { title: 'fs [KPa]', range: [0, 0.5], ticks: 'outside', autotick: false, tick0: 0,dtick: 0.05, showgrid: true,
        zeroline: true,
        showline: true,
        mirror: 'ticks',
        gridcolor: '#bdbdbd',
        gridwidth: 1},
      yaxis: { title: 'Depth [m]', tick0: 0,
      dtick: 1, autorange: 'reversed', showgrid: true,
      zeroline: true,
      showline: true,
      mirror: 'ticks',
      gridcolor: '#bdbdbd',
      gridwidth: 1},
      legend: {
      x: 0, // Place the legend at the horizontal center
      y: -0.1, // Position the legend below the chart (negative value)
      orientation: 'h' // Set the legend orientation to horizontal
    },
    height:650,
    margin: {
      l: 25,
      r:20, t: 30, b:55},
     showlegend: true,
      title: { text: 'fs vs depth', font: { color: 'black' } }
    }, { responsive: true });

    // Plot qc data
    Plotly.newPlot('qc', qcData, {
      xaxis: { title: 'qc [MPa]', range: [0, 60], ticks: 'outside', autotick: false,tick0: 0, dtick: 7, showgrid: true,
        zeroline: true,
        showline: true,
        mirror: 'ticks',
        gridcolor: '#bdbdbd',
        gridwidth: 1},
        yaxis: { title: 'Depth [m]', tick0: 0,
        dtick: 1, autorange: 'reversed', showgrid: true,
        zeroline: true,
        showline: true,
        mirror: 'ticks',
        gridcolor: '#bdbdbd',
        gridwidth: 1},
        legend: {
        x: 0, // Place the legend at the horizontal center
        y: -0.1, // Position the legend below the chart (negative value)
        orientation: 'h' // Set the legend orientation to horizontal
      },
      height:650,
      showlegend: true,
      margin: {
          l: 25,
          r:20, t: 30, b:55},

      title: { text: 'qc vs depth', font: { color: 'black' } }
    }, { responsive: true });
  });
}

  logout(): void {
    localStorage.removeItem('token');
      this.router.navigate(['/']);
  }


}
