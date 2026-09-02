"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { isAuthenticated, getUserRole } from "@/lib/auth";
import styles from "./page.module.css";
import { ShieldAlert, Server, BarChart2, Activity } from "lucide-react";

export default function AdminPanel() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState<string | null>(null);
  
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [pendingChallenges, setPendingChallenges] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login/government");
      return;
    }
    const currentRole = getUserRole();
    if (currentRole !== 'GOVERNMENT' && currentRole !== 'PLATFORM_ADMIN') {
      router.push("/dashboard");
      return;
    }
    setRole(currentRole);
    fetchAdminData();
  }, [router]);

  const fetchAdminData = async () => {
    try {
      // 1. Fetch system health
      const healthRes = await api.get("/health");
      setSystemHealth(healthRes.data);

      // 2. Fetch pending verifications
      const challengesRes = await api.get("/challenges/?status=SUBMITTED&page_size=10");
      setPendingChallenges(challengesRes.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (id: string, action: 'approve' | 'reject') => {
    try {
      await api.post(`/challenges/${id}/verify`, { action });
      fetchAdminData(); // Refresh list
    } catch (err) {
      alert("Action failed");
    }
  };

  if (loading) return <div className={styles.loading}>Loading Admin Panel...</div>;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Government Admin Panel</h1>
        <p>Oversee verifications, fairness metrics, and system health.</p>
      </div>

      <div className={styles.grid}>
        <div className={styles.mainCol}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <ShieldAlert size={20} className={styles.iconWarning} />
              <h2>Verification Queue</h2>
            </div>
            
            {pendingChallenges.length === 0 ? (
              <div className={styles.emptyState}>All caught up! No pending grievances.</div>
            ) : (
              <div className={styles.queueList}>
                {pendingChallenges.map(challenge => (
                  <div key={challenge.id} className={styles.queueItem}>
                    <div className={styles.queueInfo}>
                      <Link href={`/challenges/${challenge.id}`} className={styles.queueTitle}>
                        {challenge.title}
                      </Link>
                      <div className={styles.queueMeta}>
                        <span className={styles.domain}>{challenge.domain}</span>
                        <span className={`${styles.severity} ${styles[challenge.severity.toLowerCase()]}`}>
                          {challenge.severity}
                        </span>
                      </div>
                    </div>
                    <div className={styles.actionGroup}>
                      <button onClick={() => handleVerify(challenge.id, 'approve')} className={styles.approveBtn}>
                        Approve
                      </button>
                      <button onClick={() => handleVerify(challenge.id, 'reject')} className={styles.rejectBtn}>
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <BarChart2 size={20} className={styles.iconPrimary} />
              <h2>Fairness & Allocation Metrics</h2>
            </div>
            <div className={styles.emptyState}>
              Charts will be populated as more challenges are matched.
            </div>
          </div>
        </div>

        <div className={styles.sideCol}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <Activity size={20} className={styles.iconSuccess} />
              <h2>System Health</h2>
            </div>
            <div className={styles.healthList}>
              <div className={styles.healthItem}>
                <span className={styles.healthLabel}>API Status</span>
                <span className={`${styles.statusBadge} ${systemHealth?.status === 'healthy' ? styles.up : styles.down}`}>
                  {systemHealth?.status === 'healthy' ? 'Operational' : 'Degraded'}
                </span>
              </div>
              <div className={styles.healthItem}>
                <span className={styles.healthLabel}>API Version</span>
                <span className={styles.healthValue}>{systemHealth?.version || 'Unknown'}</span>
              </div>
              <div className={styles.healthItem}>
                <span className={styles.healthLabel}>AI Classifier</span>
                <span className={`${styles.statusBadge} ${styles.up}`}>Online</span>
              </div>
            </div>
          </div>
          
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <Server size={20} className={styles.iconPrimary} />
              <h2>IP Licenses</h2>
            </div>
            <div className={styles.summaryBox}>
              <div className={styles.summaryNumber}>0</div>
              <div className={styles.summaryText}>Active Royalty-Free Licenses Granted to Government</div>
            </div>
            <Link href="/ip-agreement" className={styles.linkBtn}>View IP Framework</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
