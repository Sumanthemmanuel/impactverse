"use client";

import { useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ShieldCheck, GraduationCap, Building2, Landmark, ArrowLeft } from "lucide-react";
import { api } from "@/lib/api";
import { setTokens } from "@/lib/auth";
import styles from "./page.module.css";

const ROLE_CONFIG = {
  citizen: { icon: ShieldCheck, title: "Citizen Portal", color: "citizen", role: "CITIZEN" },
  student: { icon: GraduationCap, title: "Student Portal", color: "student", role: "STUDENT" },
  university: { icon: Building2, title: "University Portal", color: "university", role: "HEI_ADMIN" },
  government: { icon: Landmark, title: "Government Portal", color: "government", role: "GOVERNMENT" },
};

export default function RoleLogin({ params }: { params: Promise<{ role: string }> }) {
  // Use React.use() to unwrap the params promise (Next.js 15+ requirement/pattern)
  const resolvedParams = use(params);
  const roleKey = resolvedParams.role as keyof typeof ROLE_CONFIG;
  const config = ROLE_CONFIG[roleKey];
  const router = useRouter();

  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!config) return <div>Portal not found</div>;

  const Icon = config.icon;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        // Use standard URLSearchParams for OAuth2PasswordRequestForm if backend uses it, 
        // but backend auth.py shows data: LoginRequest JSON
        const res = await api.post("/auth/login", {
          email: formData.email,
          password: formData.password,
        });
        setTokens(res.data.access_token, res.data.refresh_token);
        
        // Fetch user to store role, simple implementation
        const meRes = await api.get("/auth/me");
        localStorage.setItem("user", JSON.stringify(meRes.data));
        
        router.push("/dashboard");
      } else {
        const res = await api.post("/auth/register", {
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
          role: config.role,
        });
        setTokens(res.data.access_token, res.data.refresh_token);
        
        const meRes = await api.get("/auth/me");
        localStorage.setItem("user", JSON.stringify(meRes.data));
        
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <Link href="/login" className={styles.backLink}>
        <ArrowLeft size={18} /> Back to Portals
      </Link>
      
      <div className={`${styles.authCard} ${styles[config.color]}`}>
        <div className={styles.header}>
          <div className={styles.iconWrapper}>
            <Icon size={32} />
          </div>
          <h1>{config.title}</h1>
          <p>{isLogin ? "Welcome back" : "Create your account"}</p>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          {!isLogin && (
            <div className={styles.inputGroup}>
              <label>Full Name</label>
              <input 
                type="text" 
                required 
                value={formData.full_name}
                onChange={e => setFormData({...formData, full_name: e.target.value})}
              />
            </div>
          )}
          
          <div className={styles.inputGroup}>
            <label>Email Address</label>
            <input 
              type="email" 
              required 
              value={formData.email}
              onChange={e => setFormData({...formData, email: e.target.value})}
            />
          </div>
          
          <div className={styles.inputGroup}>
            <label>Password</label>
            <input 
              type="password" 
              required 
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
            />
          </div>

          {!isLogin && roleKey === "student" && (
            <div className={styles.ipAgreementInfo}>
              <p>By registering, you acknowledge our Dual License IP Framework where you retain commercial rights while granting the government a royalty-free license for public service.</p>
            </div>
          )}

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? "Please wait..." : (isLogin ? "Sign In" : "Register")}
          </button>
        </form>

        <div className={styles.toggle}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setIsLogin(!isLogin)} className={styles.toggleBtn}>
            {isLogin ? "Register" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}
