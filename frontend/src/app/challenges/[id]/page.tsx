"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, MapPin, AlertTriangle, Bot, ShieldCheck, Clock, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { getUserRole } from "@/lib/auth";
import styles from "./page.module.css";

export default function ChallengeDetail({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const challengeId = resolvedParams.id;
  
  const [challenge, setChallenge] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    setRole(getUserRole());
    fetchChallenge();
  }, [challengeId]);

  const fetchChallenge = async () => {
    try {
      const res = await api.get(`/challenges/${challengeId}`);
      setChallenge(res.data);
    } catch (err) {
      setError("Failed to load challenge details.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (action: 'approve' | 'reject') => {
    try {
      await api.post(`/challenges/${challengeId}/verify`, { action });
      fetchChallenge(); // Refresh
    } catch (err) {
      alert("Verification failed");
    }
  };

  if (loading) return <div className={styles.loading}>Loading challenge...</div>;
  if (error) return <div className={styles.error}>{error}</div>;
  if (!challenge) return <div className={styles.error}>Challenge not found</div>;

  return (
    <div className={styles.page}>
      <Link href="/dashboard" className={styles.backLink}>
        <ArrowLeft size={18} /> Back to Dashboard
      </Link>

      <div className={styles.header}>
        <div className={styles.metaRow}>
          <span className={`${styles.statusBadge} ${styles[challenge.status.toLowerCase()]}`}>
            {challenge.status}
          </span>
          <span className={styles.date}>
            <Clock size={14} /> {new Date(challenge.created_at).toLocaleDateString()}
          </span>
        </div>
        <h1>{challenge.title}</h1>
        <div className={styles.locationInfo}>
          <MapPin size={16} /> 
          {challenge.district ? `${challenge.district}, Jharkhand` : 'Location unspecified'}
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.mainCol}>
          <div className={styles.card}>
            <h2>Description</h2>
            <p className={styles.narrative}>{challenge.narrative}</p>
          </div>

          <div className={styles.card}>
            <h2>Media & Evidence</h2>
            {challenge.media && challenge.media.length > 0 ? (
              <div className={styles.mediaGrid}>
                {challenge.media.map((m: any) => (
                  <div key={m.id} className={styles.mediaItem}>
                    {/* Placeholder for actual media rendering */}
                    <div className={styles.mediaPlaceholder}>
                      <FileText size={32} />
                      <span>{m.file_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className={styles.emptyText}>No media attached to this grievance.</p>
            )}
          </div>
        </div>

        <div className={styles.sideCol}>
          <div className={`${styles.card} ${styles.aiCard}`}>
            <div className={styles.cardHeader}>
              <Bot size={20} />
              <h2>AI Analysis</h2>
            </div>
            
            <div className={styles.aiMetrics}>
              <div className={styles.metric}>
                <span className={styles.label}>Primary Domain</span>
                <span className={styles.value}>{challenge.domain}</span>
              </div>
              <div className={styles.metric}>
                <span className={styles.label}>Severity Level</span>
                <span className={`${styles.value} ${styles[challenge.severity.toLowerCase()]}`}>
                  {challenge.severity}
                </span>
              </div>
              {challenge.ai_confidence && (
                <div className={styles.metric}>
                  <span className={styles.label}>AI Confidence</span>
                  <div className={styles.progressTrack}>
                    <div 
                      className={styles.progressFill} 
                      style={{ width: `${challenge.ai_confidence * 100}%` }}
                    />
                  </div>
                  <span className={styles.progressText}>{(challenge.ai_confidence * 100).toFixed(1)}%</span>
                </div>
              )}
            </div>
          </div>

          {role === 'GOVERNMENT' && challenge.status === 'SUBMITTED' && (
            <div className={styles.card}>
              <h2>Verification Action</h2>
              <p className={styles.infoText}>As a government verifier, review the details above and approve or reject this challenge for university matching.</p>
              <div className={styles.actionButtons}>
                <button onClick={() => handleVerify('approve')} className={styles.approveBtn}>
                  <ShieldCheck size={18} /> Approve
                </button>
                <button onClick={() => handleVerify('reject')} className={styles.rejectBtn}>
                  <AlertTriangle size={18} /> Reject
                </button>
              </div>
            </div>
          )}

          {role === 'STUDENT' && challenge.status === 'VALIDATED' && (
            <div className={styles.card}>
              <h2>Accept Challenge</h2>
              <p className={styles.infoText}>Ready to solve this? Remember, accepting requires agreeing to the Dual License IP Framework.</p>
              <Link href={`/ip-agreement?challenge=${challenge.id}`} className={styles.primaryBtn}>
                Review IP Agreement & Accept
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
