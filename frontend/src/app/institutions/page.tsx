"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import styles from "./page.module.css";
import { Building2, MapPin, Users, CheckCircle2 } from "lucide-react";

export default function InstitutionsPage() {
  const [institutions, setInstitutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstitutions();
  }, []);

  const fetchInstitutions = async () => {
    try {
      const res = await api.get("/institutions/");
      setInstitutions(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>Loading institutions...</div>;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Partner Universities</h1>
        <p>Higher Education Institutions driving innovation in Jharkhand.</p>
      </div>

      <div className={styles.grid}>
        {institutions.map(inst => (
          <div key={inst.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper}>
                <Building2 size={24} />
              </div>
              <div className={styles.meta}>
                {inst.is_verified && (
                  <span className={styles.verified}>
                    <CheckCircle2 size={14} /> Verified Partner
                  </span>
                )}
              </div>
            </div>
            
            <h2>{inst.name}</h2>
            <div className={styles.details}>
              <span className={styles.detailItem}>
                <MapPin size={16} /> {inst.district}, {inst.state}
              </span>
              <span className={styles.detailItem}>
                <Users size={16} /> {inst.student_count || 0} Students
              </span>
            </div>

            <div className={styles.expertiseSection}>
              <h3>Core Expertise</h3>
              <div className={styles.tags}>
                {inst.domains?.map((d: string) => (
                  <span key={d} className={styles.tag}>{d}</span>
                )) || <span className={styles.tag}>General</span>}
              </div>
            </div>

            <Link href={`/institutions/${inst.id}`} className={styles.viewBtn}>
              View Profile
            </Link>
          </div>
        ))}

        {institutions.length === 0 && (
          <div className={styles.emptyState}>
            <p>No institutions registered yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
