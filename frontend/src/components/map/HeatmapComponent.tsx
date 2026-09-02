"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
// @ts-ignore - leaflet.heat doesn't have good type definitions
import "leaflet.heat";

export default function HeatmapComponent({ points }: { points: any[] }) {
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (!mapRef.current) {
      // Initialize map centered on Jharkhand
      mapRef.current = L.map("map", {
        center: [23.6102, 85.2799],
        zoom: 7,
      });

      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://carto.com/">CartoDB</a>',
        subdomains: "abcd",
        maxZoom: 19,
      }).addTo(mapRef.current);
    }

    if (mapRef.current && points.length > 0) {
      // Format points for leaflet.heat: [lat, lng, intensity]
      const heatData = points.map(p => [p.latitude, p.longitude, p.count * 10]);

      if (heatLayerRef.current) {
        mapRef.current.removeLayer(heatLayerRef.current);
      }

      heatLayerRef.current = (L as any).heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        gradient: {
          0.4: '#6366f1',
          0.6: '#8b5cf6',
          0.8: '#f59e0b',
          1.0: '#ef4444'
        }
      }).addTo(mapRef.current);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [points]);

  return <div id="map" style={{ width: "100%", height: "100%", borderRadius: "16px" }} />;
}
