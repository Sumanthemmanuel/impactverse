import Link from "next/link";
import { ArrowLeft, CheckCircle2, ShieldAlert } from "lucide-react";
import styles from "./page.module.css";

export default function IPAgreement() {
  return (
    <div className={styles.page}>
      <Link href="/" className={styles.backLink}>
        <ArrowLeft size={18} /> Back to Home
      </Link>
      
      <div className={styles.header}>
        <h1>Dual License IP Framework</h1>
        <p>A fair, transparent intellectual property agreement for SIH 2026</p>
      </div>

      <div className={styles.grid}>
        <div className={styles.licenseCard}>
          <div className={`${styles.cardHeader} ${styles.govtHeader}`}>
            <h2>Government License</h2>
            <div className={styles.badge}>Royalty-Free</div>
          </div>
          <div className={styles.cardBody}>
            <p className={styles.summary}>
              The Government of Jharkhand receives a perpetual, royalty-free license to use the solution for public service.
            </p>
            <ul className={styles.rightsList}>
              <li><CheckCircle2 size={18} className={styles.check} /> Deploy solution statewide</li>
              <li><CheckCircle2 size={18} className={styles.check} /> Modify for public service needs</li>
              <li><CheckCircle2 size={18} className={styles.check} /> Internal governmental use</li>
              <li><ShieldAlert size={18} className={styles.alert} /> Cannot resell the software</li>
              <li><ShieldAlert size={18} className={styles.alert} /> Cannot sublicense commercially</li>
            </ul>
          </div>
        </div>

        <div className={styles.licenseCard}>
          <div className={`${styles.cardHeader} ${styles.studentHeader}`}>
            <h2>Student Rights</h2>
            <div className={styles.badge}>Commercial Rights</div>
          </div>
          <div className={styles.cardBody}>
            <p className={styles.summary}>
              Student creators retain full ownership and commercial rights to their innovative solutions.
            </p>
            <ul className={styles.rightsList}>
              <li><CheckCircle2 size={18} className={styles.check} /> Patent the innovation</li>
              <li><CheckCircle2 size={18} className={styles.check} /> License commercially to private entities</li>
              <li><CheckCircle2 size={18} className={styles.check} /> Form a startup or company</li>
              <li><CheckCircle2 size={18} className={styles.check} /> Seek external investors</li>
              <li><ShieldAlert size={18} className={styles.alert} /> Cannot revoke government license</li>
            </ul>
          </div>
        </div>
      </div>

      <div className={styles.infoBox}>
        <h3>Why this model?</h3>
        <p>Traditional hackathons often demand full IP handover, discouraging students from building truly scalable businesses. Our dual-license model ensures the government gets its problems solved for free, while students are incentivized to build world-class, commercializable tech startups right here in Jharkhand.</p>
      </div>
    </div>
  );
}
