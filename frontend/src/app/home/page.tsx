import Link from "next/link";
import Image from "next/image";
import styles from "./page.module.css";
import {
  ArrowRight,
  BookOpen,
  Stethoscope,
  Droplets,
  Leaf,
  Zap,
  Building2,
  ShieldCheck,
  HeartHandshake,
  Briefcase,
  Search,
  FileText,
  Brain,
  Users,
} from "lucide-react";

const DOMAINS = [
  { name: "Education",         icon: BookOpen,       color: "#3b82f6",  count: 34 },
  { name: "Healthcare",        icon: Stethoscope,    color: "#ef4444",  count: 28 },
  { name: "Water Resources",   icon: Droplets,       color: "#06b6d4",  count: 19 },
  { name: "Environment",       icon: Leaf,           color: "#10b981",  count: 41 },
  { name: "Energy",            icon: Zap,            color: "#f59e0b",  count: 15 },
  { name: "Urban Development", icon: Building2,      color: "#6366f1",  count: 22 },
  { name: "Public Admin",      icon: ShieldCheck,    color: "#64748b",  count: 37 },
  { name: "Rural Livelihoods", icon: HeartHandshake, color: "#ec4899",  count: 26 },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    icon: FileText,
    title: "Citizen Reports",
    desc: "A citizen submits an issue with photo, location, and a brief description via the portal.",
    color: "#10b981",
  },
  {
    step: "02",
    icon: Brain,
    title: "AI Classifies",
    desc: "Our AI model tags the domain, severity, and district — and checks for duplicates automatically.",
    color: "#3b82f6",
  },
  {
    step: "03",
    icon: Users,
    title: "Students Solve",
    desc: "Matched student teams from Jharkhand colleges collaborate and deploy real-world solutions.",
    color: "#f59e0b",
  },
];

export default function Home() {
  return (
    <main className={styles.main}>
      {/* ── Hero Banner ─────────────────────────────────────────────── */}
      <section className={styles.heroBanner}>
        <Image
          src="/banner.jpeg"
          alt="Government of Jharkhand Official Banner"
          fill
          priority
          className={styles.bannerImg}
          sizes="100vw"
        />
        <div className={styles.bannerOverlay} />
        <div className={styles.bannerContent}>
          <h1 className={styles.bannerTitle}>Building a Stronger,<br />Sustainable Jharkhand</h1>
          <p className={styles.bannerTagline}>Powered by citizen voice · student innovation · government action</p>
        </div>
        <div className={styles.searchFloat}>
          <div className={styles.searchBar}>
            <Search className={styles.searchIcon} size={20} />
            <input type="text" placeholder="Search services, domains, or public records…" />
            <button className={styles.searchBtn}>Search</button>
          </div>
        </div>
      </section>

      {/* ── Portal Cards ─────────────────────────────────────────────── */}
      <section className={styles.portalsSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Digital Portals</h2>
          <div className={styles.portalsGrid}>
            <Link href="/login/citizen" className={`${styles.portalCard} ${styles.citizenCard}`}>
              <div className={styles.portalBg}>
                <Image src="/portals_bg.jpg" alt="" fill className={styles.portalBgImg} sizes="300px" />
              </div>
              <div className={styles.portalCardInner}>
                <div className={styles.portalIcon} style={{ background: "rgba(16,185,129,0.15)", color: "#10b981" }}>
                  <ShieldCheck size={28} />
                </div>
                <h3>Citizen Portal</h3>
                <p>Report issues &amp; track progress</p>
                <span className={styles.portalArrow}><ArrowRight size={16} /></span>
              </div>
            </Link>

            <Link href="/login/student" className={`${styles.portalCard} ${styles.studentCard}`}>
              <div className={styles.portalBg}>
                <Image src="/portals_bg.jpg" alt="" fill className={styles.portalBgImg} sizes="300px" />
              </div>
              <div className={styles.portalCardInner}>
                <div className={styles.portalIcon} style={{ background: "rgba(59,130,246,0.15)", color: "#3b82f6" }}>
                  <BookOpen size={28} />
                </div>
                <h3>Innovator Portal</h3>
                <p>Solve problems for your state</p>
                <span className={styles.portalArrow}><ArrowRight size={16} /></span>
              </div>
            </Link>

            <Link href="/login/government" className={`${styles.portalCard} ${styles.govCard}`}>
              <div className={styles.portalBg}>
                <Image src="/portals_bg.jpg" alt="" fill className={styles.portalBgImg} sizes="300px" />
              </div>
              <div className={styles.portalCardInner}>
                <div className={styles.portalIcon} style={{ background: "rgba(239,68,68,0.15)", color: "#ef4444" }}>
                  <Building2 size={28} />
                </div>
                <h3>Government Portal</h3>
                <p>Verify &amp; assign challenges</p>
                <span className={styles.portalArrow}><ArrowRight size={16} /></span>
              </div>
            </Link>

            <Link href="/login/industry" className={`${styles.portalCard} ${styles.industryCard}`}>
              <div className={styles.portalBg}>
                <Image src="/portals_bg.jpg" alt="" fill className={styles.portalBgImg} sizes="300px" />
              </div>
              <div className={styles.portalCardInner}>
                <div className={styles.portalIcon} style={{ background: "rgba(168,85,247,0.15)", color: "#a855f7" }}>
                  <Briefcase size={28} />
                </div>
                <h3>Industry Portal</h3>
                <p>Sponsor scalable solutions</p>
                <span className={styles.portalArrow}><ArrowRight size={16} /></span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Domains Grid ─────────────────────────────────────────────── */}
      <section className={styles.domainsSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Information and Services</h2>
          <div className={styles.domainsGrid}>
            {DOMAINS.map((domain) => (
              <Link
                href={`/challenges?domain=${domain.name}`}
                key={domain.name}
                className={styles.domainCard}
                style={{ "--domain-color": domain.color } as React.CSSProperties}
              >
                <div
                  className={styles.domainIcon}
                  style={{ color: domain.color, background: `${domain.color}18` }}
                >
                  <domain.icon size={26} />
                </div>
                <div className={styles.domainContent}>
                  <div>
                    <h3>{domain.name}</h3>
                    <span className={styles.domainCount}>{domain.count} Active Issues</span>
                  </div>
                  <ArrowRight size={16} className={styles.domainArrow} />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────────────── */}
      <section className={styles.howSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>How It Works</h2>
          <div className={styles.howGrid}>
            {HOW_IT_WORKS.map((h, i) => (
              <div key={i} className={styles.howCard}>
                <div className={styles.howStep} style={{ color: h.color }}>{h.step}</div>
                <div className={styles.howIcon} style={{ background: `${h.color}15`, color: h.color }}>
                  <h.icon size={28} />
                </div>
                <h3 className={styles.howTitle}>{h.title}</h3>
                <p className={styles.howDesc}>{h.desc}</p>
                {i < HOW_IT_WORKS.length - 1 && <div className={styles.howConnector} />}
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
