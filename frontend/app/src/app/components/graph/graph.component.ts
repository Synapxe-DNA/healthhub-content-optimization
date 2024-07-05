import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import * as d3 from 'd3';


interface Node {
  id: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface Link {
  source: string | Node;
  target: string | Node;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}





@Component({
  selector: 'app-graph',
  standalone: true,
  imports: [],
  templateUrl: './graph.component.html',
  styleUrl: './graph.component.css'
})
export class GraphComponent implements OnInit, AfterViewInit{

  @ViewChild('graphContainer', {static: true}) graphContainer!: ElementRef

  data:GraphData = {
    nodes: [
      { id: 'A' },
      { id: 'B' },
      { id: 'C' },
      { id: 'D' },
      { id: 'E' },
      { id: 'F' },
      { id: 'G' },
    ],
    links: [
      { source: 'A', target: 'B' },
      { source: 'A', target: 'C' }
    ]
  }

  //
  // constructor() {
  // }

  ngOnInit() {
    console.log("graph init")
  }

  ngAfterViewInit() {
    this.createGraph()
  }

  private createGraph(){

    const width = this.graphContainer.nativeElement.clientWidth
    const height = this.graphContainer.nativeElement.clientHeight

    const color = d3.scaleOrdinal(d3.schemeCategory10)
    const nodes = this.data.nodes.map(d => ({...d}))
    const links = this.data.links.map(d => ({...d}))


    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id((d:any) => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width/2, height/2))
        .on("tick", ticked)



    // Create the SVG container.
    const svg = d3.select(this.graphContainer.nativeElement).append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    const container = svg.append("g")

    const zoomHandler = d3.zoom()
        .on("zoom", (event) => {
      container.attr("transform", event.transform)
    })

    svg.call(zoomHandler as any)

    // Add a line for each link, and a circle for each node.
    const link = container.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll()
        .data(links)
        .join("line")
        .attr("stroke-width", (d:any) => Math.sqrt(d.value));

    const node = container.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .selectAll()
        .data(nodes)
        .join("circle")
        .attr("r", 5)
        .attr("fill", (d:any) => color(d.group))
        .on("click", (event:any, d:any) => {
          console.log(event, d)
        })

    node.append("title")
        .text(d => d.id);

    // Add a drag behavior.
    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended) as any);

    // Set the position attributes of links and nodes each time the simulation ticks.
    function ticked() {
      link
          .attr("x1", (d:any) => d.source.x)
          .attr("y1", (d:any) => d.source.y)
          .attr("x2", (d:any) => d.target.x)
          .attr("y2", (d:any) => d.target.y);

      node
          .attr("cx", (d:any) => d.x)
          .attr("cy", (d:any) => d.y);
    }

    // Reheat the simulation when drag starts, and fix the subject position.
    function dragstarted(event:any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.sourceEvent.stopPropagation()
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag.
    function dragged(event:any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends.
    // Unfix the subject position now that it’s no longer being dragged.
    function dragended(event:any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  }

}
