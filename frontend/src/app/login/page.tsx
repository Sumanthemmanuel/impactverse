import Link from "next/link";
import styles from "./page.module.css";
import { ShieldCheck, GraduationCap, Building2, Landmark } from "lucide-react";

export default function LoginHub() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Select Your Portal</h1>
        <p>Choose the portal that matches your role in Impactverse.</p>
      </div>

      <div className={styles.grid}>
        <Link href="/login/citizen" className={`${styles.card} ${styles.citizen}`}>
          <div className={styles.iconWrapper}>
            <ShieldCheck size={32} />
          </div>
          <h2>Citizen</h2>
          <p>Submit grievances, track status, and view community impact.</p>
        </Link>

        <Link href="/login/student" className={`${styles.card} ${styles.student}`}>
          <div className={styles.iconWrapper}>
            <GraduationCap size={32} />
          </div>
          <h2>Student</h2>
          <p>Accept challenges, sign IP agreements, and build solutions.</p>
        </Link>

        <Link href="/login/university" className={`${styles.card} ${styles.university}`}>
          <div className={styles.iconWrapper}>
            <Building2 size={32} />
          </div>
          <h2>University</h2>
          <p>Manage departments, review AI matches, and oversee student teams.</p>
        </Link>

        <Link href="/login/government" className={`${styles.card} ${styles.government}`}>
          <div className={styles.iconWrapper}>
            <Landmark size={32} />
          </div>
          <h2>Government</h2>
          <p>Verify challenges, monitor fairness, and deploy solutions.</p>
        </Link>
      </div>
    </div>
  );
}
