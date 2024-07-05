import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ColourService {

  private memoizedLabelColours: {[key:string]:string} = {}

  constructor() { }

  /**
   * Method to hash a string into an int [1, 360]
   * This is used to generate a hashed Hue value used in HSL
   * @param label {string}
   * @private
   */
  private stringHash(label:string): number {
    let hash = 0
    for (let i = 0; i < label.length; i++) {
      hash += label.charCodeAt(i) * i
    }
    return (hash % 360) + 1
  }


  /**
   * Method to produce a hashed HSL that is formatted for Fabric.
   * This method also uses memoization to speed up calculations to Theta(1)
   * @param label {string}
   */
  stringHSL(label:string): string {
    if(this.memoizedLabelColours.hasOwnProperty(label)){
      return this.memoizedLabelColours[label]
    }

    const h = this.stringHash(label)
    const s = 70
    const l = 45
    const a = 20

    const formattedHSL = `hsla(${h}, ${s}%, ${l}%, ${a}%)`
    this.memoizedLabelColours[label] = formattedHSL
    return formattedHSL
  }


  intensityHSL(val:number, lower:number=0, upper:number=1):string {
    if(lower>upper){throw "Upper value has to be greater than lower value!"}

    const h = ((Math.max(val, lower)/upper) * 120).toFixed(0)
    const s = 70
    const l = 45
    const a = 20

    return `hsla(${h}, ${s}%, ${l}%, ${a}%)`
  }



}
