"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { isAuthenticated, getUserRole } from "@/lib/auth";
import { api } from "@/lib/api";
import styles from "./page.module.css";
import { Activity, Clock, CheckCircle2, ShieldCheck, FileText, Bot } from "lucide-react";

import { supabase } from "@/lib/supabase";

export default function Dashboard() {
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, pending: 0, matched: 0, completed: 0 });
  const [recentChallenges, setRecentChallenges] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    setRole(getUserRole());
    fetchDashboardData();

    // Set up Realtime Subscription
    const channel = supabase
      .channel('schema-db-changes')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'challenges' },
        (payload) => {
          console.log('New challenge received!', payload);
          setRecentChallenges((prev) => [payload.new, ...prev].slice(0, 5));
          setStats((prev) => ({
            ...prev,
            total: prev.total + 1,
            pending: prev.pending + 1
          }));
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [router]);

  const fetchDashboardData = async () => {
    try {
      const { data, error, count } = await supabase
        .from('challenges')
        .select('*', { count: 'exact' })
        .order('created_at', { ascending: false })
        .limit(5);

      if (error) throw error;

      if (data) {
        setRecentChallenges(data);
      }
      
      if (count !== null) {
        setStats(prev => ({ ...prev, total: count }));
      }
    } catch (err) {
      console.error("Supabase fetch error:", err);
      // Fallback to empty if db not setup
      setRecentChallenges([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>Loading dashboard...</div>;

  const renderRoleGreeting = () => {
    switch (role) {
      case "CITIZEN": return "Welcome back, Citizen. Thank you for shaping your community.";
      case "STUDENT": return "Welcome, Innovator. Ready to solve real-world problems?";
      case "HEI_ADMIN": return "Welcome, University Admin. Review your latest AI matches.";
      case "GOVERNMENT": return "Welcome, Official. Overview of statewide challenges.";
      case "INDUSTRY": return "Welcome, Corporate Partner. Discover ideas to invest in.";
      default: return "Welcome to your dashboard.";
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Dashboard</h1>
        <p>{renderRoleGreeting()}</p>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIconWrapper}><Activity size={24} /></div>
          <div>
            <h3>Total Challenges</h3>
            <div className={styles.statValue}>{stats.total}</div>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIconWrapper} style={{ color: "var(--warning)", background: "rgba(245,158,11,0.1)" }}><Clock size={24} /></div>
          <div>
            <h3>Pending</h3>
            <div className={styles.statValue}>{stats.pending}</div>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIconWrapper} style={{ color: "var(--accent-student)", background: "rgba(59,130,246,0.1)" }}><Bot size={24} /></div>
          <div>
            <h3>AI Matched</h3>
            <div className={styles.statValue}>{stats.matched}</div>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIconWrapper} style={{ color: "var(--success)", background: "rgba(16,185,129,0.1)" }}><CheckCircle2 size={24} /></div>
          <div>
            <h3>Deployed</h3>
            <div className={styles.statValue}>{stats.completed}</div>
          </div>
        </div>
      </div>

      <div className={styles.mainContent}>
        <div className={styles.challengesPanel}>
          <div className={styles.panelHeader}>
            <h2>Recent Challenges</h2>
            <Link href="/challenges" className={styles.viewAll}>View All</Link>
          </div>
          
          <div className={styles.challengeList}>
            {recentChallenges.map(challenge => (
              <Link href={`/challenges/${challenge.id}`} key={challenge.id} className={styles.challengeRow}>
                <div className={styles.challengeInfo}>
                  <h4>{challenge.title}</h4>
                  <span className={styles.domain}>{challenge.domain} • {challenge.district || 'Jharkhand'}</span>
                  {challenge.proposed_solution && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', borderLeft: '2px solid var(--primary)', paddingLeft: '0.5rem' }}>
                      <strong>💡 Proposed Solution:</strong> {challenge.proposed_solution.length > 50 ? challenge.proposed_solution.substring(0, 50) + '...' : challenge.proposed_solution}
                    </div>
                  )}
                </div>
                <div className={styles.challengeMeta}>
                  <span className={`${styles.statusBadge} ${styles[challenge.status.toLowerCase()]}`}>
                    {challenge.status}
                  </span>
                  <span className={`${styles.severityBadge} ${styles[challenge.severity.toLowerCase()]}`}>
                    {challenge.severity}
                  </span>
                </div>
              </Link>
            ))}
            {recentChallenges.length === 0 && (
              <div className={styles.emptyState}>
                <FileText size={48} className={styles.emptyIcon} />
                <p>No challenges found.</p>
              </div>
            )}
          </div>
        </div>

        <div className={styles.sidePanel}>
          {role === 'STUDENT' && (
            <div className={styles.actionCard}>
              <h3>IP Agreements</h3>
              <p>You have 0 pending agreements to sign.</p>
              <Link href="/ip-agreement" className={styles.actionBtn}>Review Dual License Framework</Link>
            </div>
          )}
          {role === 'CITIZEN' && (
            <div className={`${styles.actionCard} ${styles.citizenActionCard}`}>
              <div className={styles.pulseGlow}></div>
              <div className={styles.citizenActionIcon}>
                <ShieldCheck size={48} />
              </div>
              <h3>Upload Grievance Report</h3>
              <p>Found a problem in your area? Tap here to snap a photo and alert the authorities immediately.</p>
              <Link href="/challenges/new" className={styles.primaryActionBtn}>
                + New Report
              </Link>
            </div>
          )}
          {role === 'GOVERNMENT' && (
            <div className={styles.actionCard}>
              <h3>Verification Queue</h3>
              <p>There are {stats.pending} challenges waiting for verification.</p>
              <Link href="/admin" className={styles.actionBtn}>Go to Verifier Panel</Link>
            </div>
          )}
          {role === 'INDUSTRY' && (
            <div className={styles.actionCard}>
              <h3>Sponsorships</h3>
              <p>Explore validated AI matches ready for corporate investment and scaling.</p>
              <Link href="/challenges" className={styles.actionBtn}>View Opportunities</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
