import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { BhdataService } from '../../services/bhdata.service';
import * as L from 'leaflet';
import { AddbhComponent } from '../addbh/addbh.component';
import {MatDialog, MatDialogRef} from '@angular/material/dialog'
import Plotly from 'plotly.js-dist-min';
import { CategoryColorService } from '../../services/category-color.service';
@Component({
  selector: 'app-bh',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterLink, RouterOutlet],
  templateUrl: './bh.component.html',
  styleUrl: './bh.component.css'
})
export class BhComponent {
  constructor(private router: Router, private bhdata: BhdataService, private dialog: MatDialog, private categoryColorService: CategoryColorService) {}
  role = localStorage.getItem('role');
  username= localStorage.getItem('username');
  map: any;
  tile: any;
parameters: string[]= ['SPT','SCR','TCR','RQD', 'UCS']
selectedParameter: string= 'SPT';
selectedBH: string =''
selectedFiles: File[] = [];
Alldata: any = []
clickCounter: { [key: number]: number } = {};
clickedBHs: { [key: number]: string } = {};
data3d: any = [];
plotAll: boolean = true;
msg= '';
allEven: boolean= true;
timer: boolean= true;
clickedBH: string= ''
uniqueDesc: any ={}
private dialogRef: MatDialogRef<AddbhComponent> | null = null;
ngOnInit(): void {
  this.Alldata = []
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
            this.uniqueDesc={}
            this.Alldata = []
            this.data3d= []
            this.clickCounter= {}
            this.clickedBHs= {}
            this.allEven= true
            this.map.eachLayer((layer: any) => {
                this.map.removeLayer(layer);
            });
            this.getBHS(); 
          };
      
          return container;
        }
      });
      
      this.map.addControl(new customControl());
      this.getBHS(); 
  }

getBHS(): void {
  
   this.bhdata.getBHs().subscribe(response => {
    //console.log(response.data)
    const bhs= response.data
    this.map.setView([24.44536842957562, 54.29436681027249], 11);
    this.tile= L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    })
    this.tile.addTo(this.map);
    const defaultIcon = L.icon({
      iconUrl: 'assets/img/bhicon.png', // Replace with an other icon to represent project
      iconSize: [15, 15], // Size of the icon [width, height]
iconAnchor: [16, 20], // Point of the icon which will correspond to marker's location [left, bottom]
popupAnchor: [0, -20]
    });
    const redIcon = L.icon({
      iconUrl: 'assets/img/bhiconn2.png', // Replace with your red icon path
      iconSize: [15, 15], // Size of the icon [width, height]
iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location [left, bottom]
popupAnchor: [0, -32]
    });
    this.map.setView([24.44536842957562, 54.29436681027249], 11);
    this.tile= L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    })
    this.tile.addTo(this.map);
    bhs.forEach((element: { [x: string]: any; }) => {
      //console.log(element['x'])
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
     this.selectedBH= element['id']; //the BH id (unique)
     this.clickedBH = element['name'];
     this.clickedBHs[+this.selectedBH]= this.clickedBH
                  if (!this.clickCounter[+this.selectedBH]) {
                    this.clickCounter[+this.selectedBH] = 0;
                  }
                  // Increment the counter
                  this.clickCounter[+this.selectedBH] += 1;
                  //console.log(this.clickCounter[this.selectedBH]);
                  if (this.clickCounter[+this.selectedBH] % 2 !== 0) {
                    (layer as L.Marker).setIcon(redIcon);
                  } else {
                    (layer as L.Marker).setIcon(defaultIcon);
                  }
                  this.plotGraphs();
                  this.plot3d();
                  this.allEven = Object.values(this.clickCounter).every(count => count % 2 === 0);

  })
}
}).addTo(this.map); 
   })
 })
}
plotGraphs2(): void {
  this.Alldata = []
  //console.log(this.clickCounter)
  Object.keys(this.clickCounter).forEach(bh => {
      this.selectedBH = bh;
      this.plotGraphs();
  
  });
}
plotGraphs(): void {
  console.log(+this.selectedBH)
  console.log(this.clickCounter[+this.selectedBH])
  
  if (this.selectedBH && this.clickCounter[+this.selectedBH] % 2 !== 0) {
    var bh= this.clickedBHs[+this.selectedBH];
    this.bhdata.getGraphs(+this.selectedBH, this.selectedParameter).subscribe((response: any) => {
      const data = response.data;
      console.log(data)
      if (data.length === 0) {
        this.msg= 'no associated ' + this.selectedParameter + ' data to the selected borehole'
        alert(this.msg)
        this.updatePlot();
      }
      else {
      this.Alldata.push({ bh: bh, data });
      //console.log(this.Alldata)
      this.updatePlot();}
    });
  } else if (this.selectedBH && this.clickCounter[+this.selectedBH] % 2 === 0) {
    
    const index = this.Alldata.findIndex((item: { bh: string; }) => 
      item.bh == this.selectedBH);
      console.log(index)
    if (index !== -1) {
      this.Alldata.splice(index, 1);
      
    }
    this.updatePlot();
  }
}
getCategoryColor(category: string): string {
  return this.categoryColorService.getColor(category) || 'unknown';
}
update3dPlot(): void {
  var traces: any= [];
  this.data3d.forEach((item: { name: string, data: any; bh: string; }) => {
    item.data.forEach((element: { [x: string]: any; }) => {
      if (!this.uniqueDesc[element['geol_desc']]) {
        this.uniqueDesc[element['geol_desc']] = this.getRandomColor(); // Add random color for new DESC
      }
      traces.push({
        x: [element['x'], element['x']],
        y: [element['y'], element['y']],
        z: [element['Elev'] - element['depthFrom'], element['Elev'] - element['depthTo']],
        mode: 'lines',
        line: {
          color: this.getCategoryColor(element['geol_desc']),
          width: 30,
        },
        name: element['name'] + ' ' + element['geol_desc'],
        type: 'scatter3d',
        showlegend: false,
      });
    })
  });
  Object.keys(this.uniqueDesc).forEach(desc => {
    traces.push({
      x: [null], // No actual points, just for the legend
      y: [null],
      z: [null],
      mode: 'lines',
      line: {
        color: this.getCategoryColor(desc),
        width: 30,
      },
      name: desc,
      type: 'scatter3d',
      showlegend: true,
    });
  });
  Plotly.newPlot('3d', traces, {
    scene: {
      
      aspectratio: { x: 2, y: 1, z: 1 },
      xaxis: {
        title: 'Easting',
        backgroundcolor: "#DDF5FC",
        gridcolor: "#686F6C",
        showbackground: true,
        showticklabels: false,
        zerolinecolor: "#686F6C",
       }, 
         yaxis: {
          title: 'Northing',
          backgroundcolor: "#DDF5FC",
          gridcolor: "#686F6C",
          showbackground: true,
          showticklabels: false,
          zerolinecolor: "#686F6C"
         }, 
         zaxis: {
          title: 'Z [m]',
          backgroundcolor: "#DDF5FC",
          gridcolor: "#686F6C",
          showbackground: true,
          zerolinecolor: "#686F6C"
         }
    },
    legend: {
      x: 0,
      y: 1,
      orientation: 'v',
    },
    margin: {
      l: 0, r: 0, b: 0, t:0
    },
    //width: 930,
    //height: 700,
    showlegend: true,
  }, { responsive: true });
}
updatePlot(): void {
  //const units = {'ISPT': ' (mm)', 'CORE..': '', '': '', '': ''}
  var minval= 0
  var maxval=0
  var minelev= 0
  var maxelev= 0
  const plots: { x: any; y: any; mode: string; marker: { symbol: string; size: number; }; name: string; }[] = [];
  console.log(this.Alldata)
  this.Alldata.forEach((item: {data: any; bh: string; }) => {
    const data = item.data;
    //console.log(name)
    const elev = data.map((row: { [x: string]: any; }) => row['elev']);
    const value = data.map((row: { [x: string]: any; }) => row['value']);
    minelev= Math.min(elev)
    maxelev= Math.max(elev)
    minval= Math.min(value)
    maxval= Math.max(value)
    plots.push({
      x: value,
      y: elev,
      mode: 'markers',
      marker: {symbol: 'square', size: 9},
      name: this.selectedParameter + ' - ' + item.bh
    });

  });

    const dict: { [key: string]: string } = {'SPT': '', 'SCR': ' [%]', 'TCR':' [%]', 'RQD':' [%]', 'UCS': ' [MPa]'}
    const dticks: { [key: string]: number } = {'SPT': 5, 'SCR': 5, 'TCR':5, 'RQD':5, 'UCS': 0.5}
    Plotly.react('plot', plots, {
      
      xaxis: { title: this.selectedParameter + dict[this.selectedParameter], showgrid: true,
        zeroline: true,
        showline: true,
        mirror: 'ticks',
        gridcolor: '#bdbdbd',
        gridwidth: 1, autotick: false, range: [minval, maxval], ticks: 'outside', tick0: 0,dtick: dticks[this.selectedParameter] },
      yaxis: { title: 'Z [m]',tick0: 0, dtick: 2, showgrid: true,
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
      showlegend: true,
      height: 700,
      margin: {
        l: 40,
        r:20, t: 25, b:50},
      title: {
        text: this.selectedParameter + dict[this.selectedParameter],
        font: {
          color: 'black'
        }
      }
    }, { responsive: true });

}
getRandomColor() {
  const getRandomValue = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

  const r = getRandomValue(210, 255); // Red: 210-255
  const g = getRandomValue(180, 230); // Green: 180-230
  const b = getRandomValue(150, 200); // Blue: 150-200

  // Convert RGB values to hex
  const toHex = (value: number) => value.toString(16).padStart(2, '0').toUpperCase();
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

plot3d(): void {
  if (this.selectedBH && this.clickCounter[+this.selectedBH] % 2 !== 0) {
    this.bhdata.get3D(+this.selectedBH).subscribe((response: any) => {
      const data = response.data;
      console.log(data)
      if (data.length === 0) {
        this.msg= 'no associated geological description data to the selected borehole'
        alert(this.msg)
      }
      else {
      this.data3d.push({ name: name, bh: this.selectedBH, data: data });
      console.log(this.data3d)
      this.update3dPlot();}
    });
  } else if (this.selectedBH && this.clickCounter[+this.selectedBH] % 2 === 0) {
    // Removing data from the plot
    const index = this.data3d.findIndex((item: { bh: string; }) => item.bh === this.selectedBH);
    if (index !== -1) {
      this.data3d.splice(index, 1);
      this.update3dPlot();
    }
  }
}


addBHs(): void {
  if (this.dialogRef) {
    this.dialogRef.close('success');
    return;
  }

  this.dialogRef = this.dialog.open(AddbhComponent, {
    width: '500px',
    disableClose: false // Allow closing by clicking outside
  
  });

  this.dialogRef.componentInstance.bhAdded.subscribe(() => {
    this.getBHS();
  });

  this.dialogRef.afterClosed().subscribe(() => {
    this.dialogRef = null; // Reset the dialogRef when the dialog is closed
  });
}
logout(): void {
    localStorage.removeItem('token');
      this.router.navigate(['/']);
  }
}
