"use client";

import { useEffect, useRef } from "react";
import type { LatLngExpression, Map as LeafletMap } from "leaflet";

type MarkerPoint = {
  id: number | string;
  lat: number;
  lng: number;
  label?: string;
};

type Props = {
  points: MarkerPoint[];
  height?: number;
};

export function ResponseMap({ points, height = 360 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      if (!containerRef.current || points.length === 0) return;
      const L = await import("leaflet");

      if (cancelled) return;

      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }

      const center: LatLngExpression = [points[0].lat, points[0].lng];
      const map = L.map(containerRef.current).setView(center, 12);
      mapRef.current = map;

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }).addTo(map);

      const icon = L.icon({
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
      });

      const bounds = L.latLngBounds([]);
      points.forEach((p) => {
        const marker = L.marker([p.lat, p.lng], { icon }).addTo(map);
        if (p.label) marker.bindPopup(p.label);
        bounds.extend([p.lat, p.lng]);
      });
      if (points.length > 1) {
        map.fitBounds(bounds.pad(0.2));
      }
    }

    init();

    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [points]);

  if (points.length === 0) {
    return (
      <div
        style={{
          height,
          display: "grid",
          placeItems: "center",
          border: "1px dashed var(--line)",
          borderRadius: 12,
          color: "var(--muted)",
          background: "rgba(0,0,0,0.15)",
        }}
      >
        No location pins yet — respondents must allow GPS when submitting.
      </div>
    );
  }

  return <div ref={containerRef} style={{ height, width: "100%" }} />;
}
