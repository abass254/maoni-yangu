"use client";

import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { api, type Survey, type SurveyListItem, type SurveyStatus } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const DEFAULT_TEMPLATE_TITLES = new Set([
  "Job Application",
  "Kenya Elections Opinion Survey",
  "Refugee Visa Intake — Canada",
  "Refugee Visa Intake — Germany",
  "Refugee Visa Intake — UK",
  "Refugee Visa Intake — Australia",
]);

const REFUGEE_TEMPLATES: {
  title: string;
  label: string;
  create: (token: string) => Promise<Survey>;
}[] = [
  {
    title: "Refugee Visa Intake — Canada",
    label: "Canada",
    create: (token) => api.createCanadaRefugeeVisaTemplate(token),
  },
  {
    title: "Refugee Visa Intake — Germany",
    label: "Germany",
    create: (token) => api.createGermanyRefugeeVisaTemplate(token),
  },
  {
    title: "Refugee Visa Intake — UK",
    label: "UK",
    create: (token) => api.createUkRefugeeVisaTemplate(token),
  },
  {
    title: "Refugee Visa Intake — Australia",
    label: "Australia",
    create: (token) => api.createAustraliaRefugeeVisaTemplate(token),
  },
];

function statusLabel(status: SurveyStatus) {
  return status === "published" ? "published" : "draft";
}

export default function DashboardPage() {
  const { token, loading, user } = useAuth();
  const router = useRouter();
  const [surveys, setSurveys] = useState<SurveyListItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [addingElections, setAddingElections] = useState(false);
  const [addingRefugeeKey, setAddingRefugeeKey] = useState<string | null>(null);
  const isSuperadmin = Boolean(user?.is_superadmin);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.replace("/login");
      return;
    }
    api
      .listSurveys(token)
      .then(setSurveys)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load surveys")
      )
      .finally(() => setBusy(false));
  }, [token, loading, router]);

  const ownSurveys = isSuperadmin
    ? surveys.filter((s) => s.owner_id === user?.id)
    : surveys;

  const hasElectionsTemplate = ownSurveys.some(
    (s) => s.title === "Kenya Elections Opinion Survey"
  );

  function prependSurvey(survey: Survey) {
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
          language: survey.language,
          created_at: survey.created_at,
          updated_at: survey.updated_at,
          question_count: survey.questions.length,
          response_count: survey.response_count,
        },
        ...prev,
      ];
    });
  }

  async function addElectionsTemplate() {
    if (!token) return;
    setAddingElections(true);
    setError("");
    try {
      const survey = await api.createKenyaElectionsTemplate(token);
      prependSurvey(survey);
      router.push(`/surveys/${survey.id}/edit`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to add elections template"
      );
    } finally {
      setAddingElections(false);
    }
  }

  async function addRefugeeTemplate(title: string, create: (token: string) => Promise<Survey>) {
    if (!token) return;
    setAddingRefugeeKey(title);
    setError("");
    try {
      const survey = await create(token);
      prependSurvey(survey);
      router.push(`/surveys/${survey.id}/edit`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to add refugee visa template"
      );
    } finally {
      setAddingRefugeeKey(null);
    }
  }

  if (loading || busy) {
    return <p style={{ color: "var(--muted)" }}>Loading surveys…</p>;
  }

  const missingRefugee = REFUGEE_TEMPLATES.filter(
    (t) => !ownSurveys.some((s) => s.title === t.title)
  );

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
            {isSuperadmin ? "All surveys" : "Your surveys"}
          </h1>
          <p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
            {isSuperadmin
              ? "Superadmin view — every questionnaire on the platform, including owner details."
              : "New accounts get job, elections, and refugee visa templates (Canada, Germany, UK, Australia) — edit, publish, and share."}
          </p>
        </div>
        {!isSuperadmin && (
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
          {missingRefugee.map((t) => (
            <button
              key={t.title}
              type="button"
              onClick={() => void addRefugeeTemplate(t.title, t.create)}
              disabled={addingRefugeeKey === t.title}
              style={secondaryBtn}
            >
              {addingRefugeeKey === t.title
                ? "Adding…"
                : `Add refugee visa (${t.label})`}
            </button>
          ))}
          <Link href="/surveys/new" style={primaryLink}>
            New survey
          </Link>
        </div>
        )}
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
          No surveys yet. Create one to get a shareable link.
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
                    {isSuperadmin && (s.owner_name || s.owner_email)
                      ? `Owner: ${s.owner_name || "—"}${s.owner_email ? ` (${s.owner_email})` : ""} · `
                      : ""}
                    {DEFAULT_TEMPLATE_TITLES.has(s.title) ? "Default template · " : ""}
                    {s.question_count} questions · {s.response_count} responses ·{" "}
                    <span style={{ color: s.status === "published" ? "var(--accent)" : "var(--warn)" }}>
                      {statusLabel(s.status)}
                    </span>
                  </p>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <Link href={`/surveys/${s.id}/edit`} style={chip}>
                    {isSuperadmin ? "View / edit" : "Edit"}
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
