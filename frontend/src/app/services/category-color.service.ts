import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CategoryColorService {
  private colors: { [key: string]: string } = {
    // Soils
    "COBBLES & BOULDERS": "#515463",
    "GRAVEL": "#b3ac8e",
    "SAND": "#f9d84d",
    "SILT": "#e39610",
    "CLAY": "#6a4312",
    "CLAY / SILT" : "#6a4312",
    "ORGANIC SAND": "#f0f772",

    //COMPOSITE SOILS
    "SILTY SAND": "#EDB72F",
  "GRAVELLY SAND": "#D5C36E",
  "CLAYEY SAND": "#815B1B",
  "SILTY GRAVEL": "#D39C3A",
  "CLAYEY GRAVEL": "#83683A",
  "SILTY GRAVELLY SAND": "#E7BA44",
  "CLAYEY GRAVELLY SAND": "#D1B247",
  "SILTY CLAY": "#7E5112",
  "GRAVELLY CLAY": "#8E7951",
  "SANDY GRAVEL": "#E3C862",
  "SILTY SANDY GRAVEL": "#C7B06E",
  "SANDY SILT": "#F3C238",
  "GRAVELLY SILT": "#CBA24F",
  "SANDY CLAY": "#9A7526",
  "SILTY SANDY GRAVELLY CLAY": "#8A6730",
  "SILTY GRAVELLY CLAY": "#8E6120",
  "SANDY GRAVELLY CLAY": "#926F2C",


    
    // Others
    "MADE GROUND / FILL": "#7d7d7d",
    "PEAT / TOPSOIL": "#99cc99",
    "CONCRETE": "#ffffff",
    "ASPHALT": "#000000",
    "LANDSLIDE / DEBRIS FLOW": "#d3d3d3",
    "PERIDOTITE": "#99cc99",
    "SOFT GYPSUM": "#6666ff",
    "CALCITE": "#ffcc99",
   "CALCISILTITE": "#fcc0ee", 
    
    // Sedimentary
    "CALCARENITE": "#f95dbf",
    "LIMESTONE": "#ceccb6",
    "PHOSPHATE": "#a8a79e",
    "CORAL": "#9d71b4",
    "CHERT": "#e6440c",
    "CONGLOMERATE": "#0c64e6",
    "BRECCIA": "#cc99ff",
    "SANDSTONE": "#f9efa8",
    "SILTSTONE": "#ffc87f",
    "CLAYSTONE": "#ba7e34",
    "MUDSTONE": "#ba7e34",
    "SHALE": "#666600",
    "MARLSTONE": "#ffffcc",
    "COAL": "#000000",
    "GYPSUM, ROCKSALT": "#77b6f0",
    
    // Igneous
    "GRANITE / GABBRO": "#ff99cc",
    "DIORITE / ANDESITE": "#99cc99",
    "BASALT / RHYOLITE": "#666666",
    
    // Metamorphic (Foliated)
    "GNEISS": "#ffff66",
    "SCHIST": "#cc9966",
    "SLATE": "#66cc33",
    
    // Metamorphic (Non-Foliated)
    "METACONGLOMERATE": "#d3d3d3",
    "MARBLE": "#cccccc",
    "HORNFELS": "#66ccff"
  };

  constructor() {}

  getColor(category: string): string | null {
    return this.colors[category.toUpperCase()] || null;
  }


}
