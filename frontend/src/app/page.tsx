import Link from "next/link";

export default function HomePage() {
  return (
    <section
      style={{
        minHeight: "72vh",
        display: "grid",
        alignContent: "center",
        gap: "1.5rem",
        padding: "2rem 0 4rem",
      }}
    >
      <p
        style={{
          margin: 0,
          color: "var(--accent)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          fontSize: "0.78rem",
          fontWeight: 600,
        }}
      >
        Your insights, tied to place
      </p>
      <h1
        style={{
          margin: 0,
          fontFamily: "var(--font-display)",
          fontSize: "clamp(2.6rem, 7vw, 4.4rem)",
          lineHeight: 1.05,
          letterSpacing: "-0.03em",
          maxWidth: "14ch",
        }}
      >
        Maoni Yangu
      </h1>
      <p
        style={{
          margin: 0,
          fontSize: "1.2rem",
          color: "var(--muted)",
          maxWidth: 520,
          lineHeight: 1.55,
        }}
      >
        Create surveys, share a link, collect answers — and capture the
        coordinates where each response was submitted.
      </p>
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
        <Link
          href="/register"
          style={{
            background: "var(--accent)",
            color: "#06261d",
            borderRadius: 999,
            padding: "0.85rem 1.4rem",
            fontWeight: 700,
          }}
        >
          Create your first survey
        </Link>
        <Link
          href="/login"
          style={{
            border: "1px solid var(--line)",
            borderRadius: 999,
            padding: "0.85rem 1.4rem",
          }}
        >
          Log in
        </Link>
      </div>
    </section>
  );
}
