import type { CSSProperties, ReactNode } from "react";

export function AuthCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div
      style={{
        maxWidth: 420,
        margin: "2rem auto",
        padding: "1.5rem",
        borderRadius: 16,
        border: "1px solid var(--line)",
        background: "rgba(22, 40, 37, 0.85)",
      }}
    >
      <h1 style={{ margin: "0 0 0.35rem", fontFamily: "var(--font-display)" }}>{title}</h1>
      <p style={{ margin: "0 0 1.25rem", color: "var(--muted)" }}>{subtitle}</p>
      {children}
    </div>
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label style={{ display: "grid", gap: 6, color: "var(--muted)", fontSize: "0.9rem" }}>
      {label}
      {children}
    </label>
  );
}

export const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 10,
  border: "1px solid var(--line)",
  background: "rgba(0,0,0,0.25)",
  color: "var(--ink)",
  padding: "0.7rem 0.85rem",
};

export const primaryBtn: CSSProperties = {
  background: "var(--accent)",
  color: "#06261d",
  border: "none",
  borderRadius: 999,
  padding: "0.75rem 1rem",
  fontWeight: 700,
  cursor: "pointer",
};
