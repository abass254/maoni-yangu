"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

export function AppHeader() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const isPublicRespond = pathname?.startsWith("/s/");

  if (isPublicRespond) return null;

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem",
        padding: "1rem 1.5rem",
        borderBottom: "1px solid var(--line)",
        backdropFilter: "blur(10px)",
        position: "sticky",
        top: 0,
        zIndex: 20,
        background: "rgba(15, 28, 26, 0.72)",
      }}
    >
      <Link href={user ? "/dashboard" : "/"} style={{ display: "flex", alignItems: "baseline", gap: "0.6rem" }}>
        <span
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "1.45rem",
            fontWeight: 600,
            letterSpacing: "-0.02em",
          }}
        >
          Maoni Yangu
        </span>
        <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
          fikradaada, goobtaada
        </span>
      </Link>
      <nav style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        {user ? (
          <>
            <Link href="/dashboard" className="nav-link">
              Xarunta
            </Link>
            <Link href="/surveys/new" className="nav-link">
              Sahan cusub
            </Link>
            <span style={{ color: "var(--muted)", fontSize: "0.9rem" }}>{user.name}</span>
            <button
              type="button"
              onClick={logout}
              style={{
                background: "transparent",
                border: "1px solid var(--line)",
                color: "var(--ink)",
                borderRadius: 999,
                padding: "0.4rem 0.9rem",
                cursor: "pointer",
              }}
            >
              Ka bax
            </button>
          </>
        ) : (
          <>
            <Link href="/login">Gal</Link>
            <Link
              href="/register"
              style={{
                background: "var(--accent)",
                color: "#06261d",
                borderRadius: 999,
                padding: "0.45rem 1rem",
                fontWeight: 600,
              }}
            >
              Bilow
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
