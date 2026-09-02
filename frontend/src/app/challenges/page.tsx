"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { Clock, ArrowRight } from "lucide-react";
import styles from "./page.module.css";

export default function ChallengesPage() {
  const [domainFilter, setDomainFilter] = useState<string | null>(null);
  const [challenges, setChallenges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const domain = params.get('domain');
    setDomainFilter(domain);
    fetchChallenges(domain);
  }, []);

  const fetchChallenges = async (domain: string | null) => {
    setLoading(true);
    try {
      let query = supabase
        .from('challenges')
        .select('*')
        .order('created_at', { ascending: false });

      if (domain) {
        query = query.eq('domain', domain);
      }

      const { data, error } = await query;
      
      if (error) throw error;
      setChallenges(data || []);
    } catch (err) {
      console.error("Error fetching challenges:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.page}>
      <div className={styles.header}>
        <h1>{domainFilter ? `${domainFilter} Issues` : 'Public Grievances'}</h1>
        <p>Explore community issues reported by citizens across Jharkhand.</p>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading challenges...</div>
      ) : challenges.length === 0 ? (
        <div className={styles.empty}>
          <h2>No issues found.</h2>
          <p>There are no reported challenges {domainFilter ? `in ${domainFilter}` : 'yet'}.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {challenges.map((challenge) => (
            <Link href={`/challenges/${challenge.id}`} key={challenge.id} className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={styles.domainBadge}>{challenge.domain}</span>
                <span className={styles.statusBadge}>{challenge.status}</span>
              </div>
              
              <h2 className={styles.cardTitle}>{challenge.title}</h2>
              <p className={styles.cardNarrative}>{challenge.description || challenge.narrative}</p>
              
              {challenge.proposed_solution && (
                <div className={styles.proposedSolutionBox}>
                  <strong>💡 Citizen's Proposed Solution:</strong>
                  <p>{challenge.proposed_solution}</p>
                </div>
              )}
              
              <div className={styles.cardFooter}>
                <div className={styles.date}>
                  <Clock size={14} />
                  {new Date(challenge.created_at).toLocaleDateString()}
                </div>
                <span className={styles.viewBtn}>View Details <ArrowRight size={14} /></span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
