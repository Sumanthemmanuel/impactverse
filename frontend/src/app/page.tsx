import Link from "next/link";
import styles from "./page.module.css";
import { ArrowRight, ShieldCheck, MapPin, Search, Cpu } from "lucide-react";

export default function LandingPage() {
  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.heroContent}>
          <div className={styles.badge}>
            <span className="text-gradient">SIH 2026 Innovation</span>
          </div>
          <h1 className={styles.title}>
            AI-Driven Grievance <br />
            <span className="text-gradient">Triage & Matching</span> Platform
          </h1>
          <p className={styles.description}>
            Revolutionizing how public grievances in Jharkhand are processed. 
            Our AI automatically categorizes complaints and matches them with university 
            student teams for innovative solutions.
          </p>
          <div className={styles.ctaGroup}>
            <Link href="/challenges/new" className={styles.primaryBtn}>
              Submit a Grievance <ArrowRight size={18} />
            </Link>
            <Link href="/login" className={styles.secondaryBtn}>
              Go to Portal
            </Link>
          </div>
        </div>
      </div>

      <section className={styles.features}>
        <div className={styles.sectionHeader}>
          <h2>How It Works</h2>
          <p>An automated end-to-end pipeline for maximum impact.</p>
        </div>
        <div className={styles.featureGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIconWrapper}>
              <MapPin className={styles.featureIcon} />
            </div>
            <h3>1. Submit</h3>
            <p>Citizens submit grievances with photos and location data via our portal.</p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIconWrapper}>
              <Cpu className={styles.featureIcon} />
            </div>
            <h3>2. AI Triage</h3>
            <p>Our NLP model categorizes the domain, detects severity, and filters spam.</p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIconWrapper}>
              <Search className={styles.featureIcon} />
            </div>
            <h3>3. Smart Match</h3>
            <p>Challenges are matched to relevant university departments across Jharkhand.</p>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.featureIconWrapper}>
              <ShieldCheck className={styles.featureIcon} />
            </div>
            <h3>4. Dual License IP</h3>
            <p>Students retain commercial rights, while govt gets a royalty-free license.</p>
          </div>
        </div>
      </section>

      <section className={styles.portals}>
        <div className={styles.sectionHeader}>
          <h2>Access Portals</h2>
          <p>Login to your dedicated portal to get started.</p>
        </div>
        <div className={styles.portalGrid}>
          <Link href="/login/citizen" className={`${styles.portalCard} ${styles.citizen}`}>
            <h3>Citizen Portal</h3>
            <p>Track your submissions</p>
          </Link>
          <Link href="/login/student" className={`${styles.portalCard} ${styles.student}`}>
            <h3>Student Portal</h3>
            <p>Find challenges to solve</p>
          </Link>
          <Link href="/login/university" className={`${styles.portalCard} ${styles.university}`}>
            <h3>University Portal</h3>
            <p>Manage teams & matches</p>
          </Link>
          <Link href="/login/government" className={`${styles.portalCard} ${styles.government}`}>
            <h3>Govt Portal</h3>
            <p>Verify and oversee</p>
          </Link>
        </div>
      </section>
    </div>
  );
}
