"use client";

import Link from "next/link";
import Image from "next/image";
import {
  UserCircle,
  ShieldCheck,
  GraduationCap,
  Briefcase,
  ArrowRight,
  MapPin,
  Brain,
  Users,
} from "lucide-react";
import styles from "./page.module.css";

const SLIDES = [
  {
    src: "/slides/india.jpeg",
    label: "Innovate. Collaborate. Transform India.",
    tag: "Mission",
  },
  {
    src: "/slides/official.jpeg",
    label: "Government-Backed Innovation Framework",
    tag: "Authority",
  },
  {
    src: "/slides/people.jpeg",
    label: "Voices of Every Citizen Matter",
    tag: "Inclusion",
  },
  {
    src: "/slides/students.jpeg",
    label: "Students Building Tomorrow's Solutions",
    tag: "Innovation",
  },
];

const ROLES = [
  {
    href: "/challenges/new",
    icon: UserCircle,
    title: "Citizen",
    desc: "Report issues, track resolution, and participate in governance.",
    accent: "var(--accent-citizen)",
    bg: "rgba(16,185,129,0.08)",
  },
  {
    href: "/login/student",
    icon: GraduationCap,
    title: "Student / Innovator",
    desc: "Take up real challenges from the community and build solutions.",
    accent: "var(--accent-student)",
    bg: "rgba(59,130,246,0.08)",
  },
  {
    href: "/login/government",
    icon: ShieldCheck,
    title: "Government Official",
    desc: "Verify issues, assign teams, and track impact at district level.",
    accent: "var(--accent-government)",
    bg: "rgba(239,68,68,0.08)",
  },
  {
    href: "/login/industry",
    icon: Briefcase,
    title: "Industry Partner",
    desc: "Sponsor scalable solutions and co-create with innovators.",
    accent: "var(--accent-industry)",
    bg: "rgba(168,85,247,0.08)",
  },
];

const STATS = [
  { icon: Brain,  label: "10 Domains" },
  { icon: MapPin, label: "24 Districts" },
  { icon: Brain,  label: "AI-Powered" },
  { icon: Users,  label: "Fair Allocation" },
];

export default function LandingPage() {
  return (
    <main className={styles.page}>
      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section className={styles.hero}>
        <Image
          src="/hero_bg.jpg"
          alt="Jharkhand hero background"
          fill
          priority
          className={styles.heroBg}
          sizes="100vw"
        />
        <div className={styles.heroOverlay} />
        <div className={styles.heroContent}>
          <div className={styles.logoRing}>
            <Image
              src="/logo.jpg"
              alt="SICP Government of Jharkhand"
              width={80}
              height={80}
              className={styles.logoImg}
              priority
            />
          </div>
          <p className={styles.heroEyebrow}>Smart India Hackathon 2026 · SIH26043</p>
          <h1 className={styles.heroTitle}>
            Societal Innovation &amp;<br />Collaborative Portal
          </h1>
          <p className={styles.heroSubtitle}>
            Empowering Jharkhand through student innovation, government action, and community voice
          </p>
          <div className={styles.heroCtas}>
            <Link href="/challenges/new" className={styles.ctaPrimary}>
              Report an Issue <ArrowRight size={18} />
            </Link>
            <Link href="/home" className={styles.ctaSecondary}>
              Explore Portal <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Official Banner ───────────────────────────────────────────── */}
      <section className={styles.bannerStrip} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#fff', padding: '1rem 0' }}>
        <Image
          src="/govt_banner.jpeg"
          alt="Government of Jharkhand"
          width={800}
          height={150}
          className={styles.bannerImg}
          style={{ objectFit: 'contain', width: 'auto', height: '150px' }}
        />
      </section>

      {/* ── Slide Grid ───────────────────────────────────────────────── */}
      <section className={styles.slideSection}>
        <div className={styles.slideGrid}>
          {SLIDES.map((s) => (
            <div key={s.src} className={styles.slidePanel}>
              <Image
                src={s.src}
                alt={s.label}
                fill
                className={styles.slidePanelImg}
                sizes="(max-width: 768px) 100vw, 50vw"
              />
              <div className={styles.slidePanelOverlay} />
              <div className={styles.slidePanelContent}>
                <span className={styles.slideTag}>{s.tag}</span>
                <p className={styles.slideLabel}>{s.label}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Who Can Use This Portal? ─────────────────────────────────── */}
      <section className={styles.rolesSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Who Can Use This Portal?</h2>
          <div className={styles.rolesGrid}>
            {ROLES.map((r) => (
              <Link key={r.href} href={r.href} className={styles.roleCard} style={{ "--card-accent": r.accent, "--card-bg": r.bg } as React.CSSProperties}>
                <div className={styles.roleIcon} style={{ background: r.bg, color: r.accent }}>
                  <r.icon size={28} />
                </div>
                <h3 className={styles.roleTitle}>{r.title}</h3>
                <p className={styles.roleDesc}>{r.desc}</p>
                <span className={styles.roleArrow} style={{ color: r.accent }}>
                  Get Started <ArrowRight size={14} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Stats Bar ────────────────────────────────────────────────── */}
      <section className={styles.statsBar}>
        <div className={styles.statsInner}>
          {STATS.map((s, i) => (
            <div key={i} className={styles.statPill}>
              <s.icon size={16} />
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer Bar ───────────────────────────────────────────────── */}
      <footer className={styles.footerBar}>
        <span>SIH26043</span>
        <span className={styles.footerDot}>·</span>
        <span>Built for Jharkhand</span>
        <span className={styles.footerDot}>·</span>
        <span>Good Governance. Inclusive Development.</span>
      </footer>
    </main>
  );
}
