"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { isAuthenticated, clearAuth } from "@/lib/auth";
import styles from "./Navbar.module.css";
import { LogOut, Map, LayoutDashboard, Menu, X } from "lucide-react";

export default function Navbar() {
  const [isLogged, setIsLogged]   = useState(false);
  const [scrolled, setScrolled]   = useState(false);
  const [menuOpen, setMenuOpen]   = useState(false);
  const router   = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setIsLogged(isAuthenticated());
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => { setMenuOpen(false); }, [pathname]);

  const handleLogout = () => {
    clearAuth();
    setIsLogged(false);
    router.push("/");
  };

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <>
      <nav className={`${styles.navbar} ${scrolled ? styles.scrolled : ""}`}
           role="navigation" aria-label="Main navigation">
        <div className={styles.container}>

          {/* ── Left: Branding ── */}
          <div className={styles.branding}>
            {/* Jharkhand state emblem */}
            <div className={styles.emblemWrap}>
              <Image
                src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Jharkhand_Rajakiya_Chihna.jpg"
                alt="Seal of Jharkhand"
                width={38}
                height={38}
                className={styles.emblem}
                unoptimized
              />
            </div>

            <Link href="/" className={styles.logoLink} aria-label="Impactverse home">
              {/* SVG logo mark */}
              <Image
                src="/impactverse-logo.svg"
                alt=""
                width={32}
                height={32}
                className={styles.logoMark}
                aria-hidden="true"
              />
              <span className={styles.logoText}>
                Impactverse
              </span>
              <span className={styles.badge} aria-label="Smart India Hackathon 2026">
                SIH &#39;26
              </span>
            </Link>
          </div>

          {/* ── Centre: Nav links (desktop) ── */}
          <div className={styles.navLinks}>
            <Link
              href="/challenges"
              className={`${styles.navLink} ${isActive("/challenges") ? styles.navLinkActive : ""}`}
            >
              Challenges
            </Link>
            <Link
              href="/heatmap"
              className={`${styles.navLink} ${isActive("/heatmap") ? styles.navLinkActive : ""}`}
            >
              <Map size={15} aria-hidden="true" />
              Impact Map
            </Link>
            <Link
              href="/institutions"
              className={`${styles.navLink} ${isActive("/institutions") ? styles.navLinkActive : ""}`}
            >
              Universities
            </Link>
          </div>

          {/* ── Right: Actions ── */}
          <div className={styles.actions}>
            {isLogged ? (
              <>
                <Link
                  href="/dashboard"
                  className={`${styles.actionBtn} ${styles.dashBtn} ${isActive("/dashboard") ? styles.dashBtnActive : ""}`}
                >
                  <LayoutDashboard size={15} aria-hidden="true" />
                  Dashboard
                </Link>
                <button
                  onClick={handleLogout}
                  className={styles.iconBtn}
                  aria-label="Sign out"
                  title="Sign out"
                >
                  <LogOut size={17} />
                </button>
              </>
            ) : (
              <Link href="/login" className={`${styles.actionBtn} ${styles.signInBtn}`}>
                Sign In
              </Link>
            )}

            {/* Chief Minister profile — desktop only */}
            <div className={styles.cmWrap} aria-label="Chief Minister of Jharkhand">
              <Image
                src="https://upload.wikimedia.org/wikipedia/commons/2/23/Hemant_Soren_2019_%28cropped%29.jpg"
                alt="Shri Hemant Soren, Chief Minister of Jharkhand"
                width={36}
                height={36}
                className={styles.cmAvatar}
                unoptimized
              />
              <div className={styles.cmCard} role="tooltip">
                <span className={styles.cmName}>Shri Hemant Soren</span>
                <span className={styles.cmTitle}>Hon&apos;ble Chief Minister, Jharkhand</span>
              </div>
            </div>

            {/* Mobile hamburger */}
            <button
              className={styles.burger}
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
            >
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* ── Mobile drawer ── */}
        <div className={`${styles.drawer} ${menuOpen ? styles.drawerOpen : ""}`}
             aria-hidden={!menuOpen}>
          <Link href="/challenges"   className={styles.drawerLink}>Challenges</Link>
          <Link href="/heatmap"      className={styles.drawerLink}><Map size={15}/> Impact Map</Link>
          <Link href="/institutions" className={styles.drawerLink}>Universities</Link>
          <div className={styles.drawerDivider} />
          {isLogged ? (
            <>
              <Link href="/dashboard" className={styles.drawerLink}>
                <LayoutDashboard size={15}/> Dashboard
              </Link>
              <button onClick={handleLogout} className={styles.drawerLink}>
                <LogOut size={15}/> Sign out
              </button>
            </>
          ) : (
            <Link href="/login" className={`${styles.drawerLink} ${styles.drawerSignIn}`}>
              Sign In / Register
            </Link>
          )}
        </div>
      </nav>

      {/* Spacer so page content is never hidden under the fixed navbar */}
      <div className={styles.navSpacer} aria-hidden="true" />
    </>
  );
}
