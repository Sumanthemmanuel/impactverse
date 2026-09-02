"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import styles from "./page.module.css";
import { Filter } from "lucide-react";

// Dynamically import the map component with SSR disabled
const HeatmapComponent = dynamic(
  () => import("@/components/map/HeatmapComponent"),
  { ssr: false, loading: () => <div className={styles.loadingMap}>Loading Map...</div> }
);

const DOMAINS = [
  "Education", "Agriculture", "Healthcare", "Water Resources", 
  "Environment", "Energy", "Urban Development", "Accessibility", 
  "Public Administration", "Rural Livelihoods"
];

export default function HeatmapPage() {
  const [points, setPoints] = useState<any[]>([]);
  const [domainFilter, setDomainFilter] = useState("");

  useEffect(() => {
    fetchHeatmapData();
  }, [domainFilter]);

  const fetchHeatmapData = async () => {
    try {
      const url = domainFilter 
        ? `/challenges/data/heatmap?domain=${encodeURIComponent(domainFilter)}`
        : `/challenges/data/heatmap`;
      const res = await api.get(url);
      setPoints(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <h1>Jharkhand Impact Map</h1>
          <p>Live visualization of grievance clusters and impact zones.</p>
        </div>
        
        <div className={styles.filterArea}>
          <div className={styles.filterGroup}>
            <Filter size={18} className={styles.filterIcon} />
            <select 
              value={domainFilter} 
              onChange={e => setDomainFilter(e.target.value)}
              className={styles.select}
            >
              <option value="">All Domains</option>
              {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className={styles.mapContainer}>
        <div className={styles.statsOverlay}>
          <div className={styles.statBox}>
            <div className={styles.statLabel}>Active Hotspots</div>
            <div className={styles.statValue}>{points.length}</div>
          </div>
          <div className={styles.statBox}>
            <div className={styles.statLabel}>Total Reports</div>
            <div className={styles.statValue}>
              {points.reduce((sum, p) => sum + p.count, 0)}
            </div>
          </div>
        </div>
        
        <HeatmapComponent points={points} />
      </div>
    </div>
  );
}
