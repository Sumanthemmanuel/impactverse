"use client";

import Link from "next/link";
import styles from "./page.module.css";
import { ShieldCheck, GraduationCap, Building2, Landmark, Briefcase } from "lucide-react";

export default function LoginHub() {
  const portals = [
    {
      id: "citizen",
      title: "Citizen",
      desc: "Report local grievances",
      icon: ShieldCheck,
      color: "citizen"
    },
    {
      id: "student",
      title: "Innovator",
      desc: "Solve issues & claim IP",
      icon: GraduationCap,
      color: "student"
    },
    {
      id: "university",
      title: "University",
      desc: "Manage & empower students",
      icon: Building2,
      color: "university"
    },
    {
      id: "government",
      title: "Government",
      desc: "Verify & deploy solutions",
      icon: Landmark,
      color: "government"
    },
    {
      id: "industry",
      title: "Industry",
      desc: "Sponsor & invest in ideas",
      icon: Briefcase,
      color: "industry"
    }
  ];

  return (
    <div className={styles.page}>
      <div className={styles.bgWrapper}>
        <div className={styles.bgOverlay} />
      </div>

      <div className={styles.container}>
        <div className={styles.header}>
          <h1>Select Your Portal</h1>
          <p>Choose your role to access the Impactverse ecosystem.</p>
        </div>

        <div className={styles.grid}>
          {portals.map((portal) => {
            const Icon = portal.icon;
            return (
              <Link href={`/login/${portal.id}`} key={portal.id} className={`${styles.portalCard} glass-panel`}>
                <div className={`${styles.iconWrapper} ${styles[portal.color]}`}>
                  <Icon size={32} />
                </div>
                <h2>{portal.title}</h2>
                <p>{portal.desc}</p>
                <div className={`${styles.glowEffect} ${styles[`glow-${portal.color}`]}`} />
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
