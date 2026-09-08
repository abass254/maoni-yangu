"use client";

import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { api, type SurveyListItem } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const DEFAULT_TEMPLATE_TITLES = new Set([
  "Job Application",
  "Kenya Elections Opinion Survey",
]);

export default function DashboardPage() {
  const { token, loading } = useAuth();
  const router = useRouter();
  const [surveys, setSurveys] = useState<SurveyListItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [addingElections, setAddingElections] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.replace("/login");
      return;
    }
    api
      .listSurveys(token)
      .then(setSurveys)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"))
      .finally(() => setBusy(false));
  }, [token, loading, router]);

  const hasElectionsTemplate = surveys.some(
    (s) => s.title === "Kenya Elections Opinion Survey"
  );

  async function addElectionsTemplate() {
    if (!token) return;
    setAddingElections(true);
    setError("");
    try {
      const survey = await api.createKenyaElectionsTemplate(token);
      setSurveys((prev) => {
        if (prev.some((s) => s.id === survey.id)) return prev;
        return [
          {
            id: survey.id,
            public_id: survey.public_id,
            title: survey.title,
            description: survey.description,
            status: survey.status,
            collect_location: survey.collect_location,
            created_at: survey.created_at,
            updated_at: survey.updated_at,
            question_count: survey.questions.length,
            response_count: survey.response_count,
          },
          ...prev,
        ];
      });
      router.push(`/surveys/${survey.id}/edit`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add elections template");
    } finally {
      setAddingElections(false);
    }
  }

  if (loading || busy) {
    return <p style={{ color: "var(--muted)" }}>Loading surveys…</p>;
  }

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
            Your surveys
          </h1>
          <p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
            New accounts get Job Application and Kenya Elections drafts — edit, publish, and share.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignSelf: "start" }}>
          {!hasElectionsTemplate && (
            <button
              type="button"
              onClick={() => void addElectionsTemplate()}
              disabled={addingElections}
              style={secondaryBtn}
            >
              {addingElections ? "Adding…" : "Add Kenya Elections template"}
            </button>
          )}
          <Link href="/surveys/new" style={primaryLink}>
            New survey
          </Link>
        </div>
      </div>

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      {surveys.length === 0 ? (
        <div
          style={{
            padding: "2rem",
            borderRadius: 16,
            border: "1px dashed var(--line)",
            color: "var(--muted)",
          }}
        >
          No surveys yet. Create one to get a shareable response link.
        </div>
      ) : (
        <div style={{ display: "grid", gap: "0.85rem" }}>
          {surveys.map((s) => (
            <article
              key={s.id}
              style={{
                display: "grid",
                gap: "0.65rem",
                padding: "1.1rem 1.2rem",
                borderRadius: 14,
                border: "1px solid var(--line)",
                background: "var(--bg-card)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
                <div>
                  <h2 style={{ margin: 0, fontSize: "1.2rem" }}>{s.title}</h2>
                  <p style={{ margin: "0.3rem 0 0", color: "var(--muted)", fontSize: "0.92rem" }}>
                    {DEFAULT_TEMPLATE_TITLES.has(s.title) ? "Default template · " : ""}
                    {s.question_count} questions · {s.response_count} responses ·{" "}
                    <span style={{ color: s.status === "published" ? "var(--accent)" : "var(--warn)" }}>
                      {s.status}
                    </span>
                  </p>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <Link href={`/surveys/${s.id}/edit`} style={chip}>
                    Edit
                  </Link>
                  <Link href={`/surveys/${s.id}/results`} style={chip}>
                    Results
                  </Link>
                  {s.status === "published" && (
                    <Link href={`/s/${s.public_id}`} style={chip} target="_blank">
                      Open link
                    </Link>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

const chip: CSSProperties = {
  border: "1px solid var(--line)",
  borderRadius: 999,
  padding: "0.4rem 0.85rem",
  fontSize: "0.9rem",
};

const primaryLink: CSSProperties = {
  background: "var(--accent)",
  color: "#06261d",
  borderRadius: 999,
  padding: "0.7rem 1.15rem",
  fontWeight: 700,
};

const secondaryBtn: CSSProperties = {
  background: "transparent",
  color: "var(--ink)",
  border: "1px solid var(--line)",
  borderRadius: 999,
  padding: "0.65rem 1.05rem",
  fontWeight: 600,
  cursor: "pointer",
};
