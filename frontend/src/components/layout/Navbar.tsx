"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { isAuthenticated, clearAuth, getUserRole } from "@/lib/auth";
import styles from "./Navbar.module.css";
import { Home, LayoutDashboard, LogIn, LogOut, Map } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const [authStatus, setAuthStatus] = useState(false);
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    setAuthStatus(isAuthenticated());
    setRole(getUserRole());
  }, [pathname]);

  const handleLogout = () => {
    clearAuth();
    setAuthStatus(false);
    setRole(null);
    window.location.href = "/";
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <span className="text-gradient">Impactverse</span>
        </Link>
        <div className={styles.links}>
          <Link href="/" className={pathname === "/" ? styles.active : ""}>
            <Home size={18} /> Home
          </Link>
          <Link href="/heatmap" className={pathname === "/heatmap" ? styles.active : ""}>
            <Map size={18} /> Map
          </Link>
          
          {authStatus ? (
            <>
              <Link href="/dashboard" className={pathname.startsWith("/dashboard") ? styles.active : ""}>
                <LayoutDashboard size={18} /> Dashboard
              </Link>
              <button onClick={handleLogout} className={styles.logoutBtn}>
                <LogOut size={18} /> Logout
              </button>
            </>
          ) : (
            <Link href="/login" className={styles.loginBtn}>
              <LogIn size={18} /> Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
