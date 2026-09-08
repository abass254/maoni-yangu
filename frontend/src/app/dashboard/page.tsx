"use client";

import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { api, type Survey, type SurveyListItem, type SurveyStatus } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const DEFAULT_TEMPLATE_TITLES = new Set([
  "Job Application",
  "Kenya Elections Opinion Survey",
  "Codsiga Fiisaha Qaxootiga — Kanada",
  "Codsiga Fiisaha Qaxootiga — Jarmalka",
  "Codsiga Fiisaha Qaxootiga — UK",
  "Codsiga Fiisaha Qaxootiga — Australia",
]);

const REFUGEE_TEMPLATES: {
  title: string;
  label: string;
  create: (token: string) => Promise<Survey>;
}[] = [
  {
    title: "Codsiga Fiisaha Qaxootiga — Kanada",
    label: "Kanada",
    create: (token) => api.createCanadaRefugeeVisaTemplate(token),
  },
  {
    title: "Codsiga Fiisaha Qaxootiga — Jarmalka",
    label: "Jarmalka",
    create: (token) => api.createGermanyRefugeeVisaTemplate(token),
  },
  {
    title: "Codsiga Fiisaha Qaxootiga — UK",
    label: "UK",
    create: (token) => api.createUkRefugeeVisaTemplate(token),
  },
  {
    title: "Codsiga Fiisaha Qaxootiga — Australia",
    label: "Australia",
    create: (token) => api.createAustraliaRefugeeVisaTemplate(token),
  },
];

function statusLabel(status: SurveyStatus) {
  return status === "published" ? "la daabacay" : "qabyo";
}

export default function DashboardPage() {
  const { token, loading } = useAuth();
  const router = useRouter();
  const [surveys, setSurveys] = useState<SurveyListItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [addingElections, setAddingElections] = useState(false);
  const [addingRefugeeKey, setAddingRefugeeKey] = useState<string | null>(null);

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
        setError(err instanceof Error ? err.message : "Waa lagu fashilmay soo raridda")
      )
      .finally(() => setBusy(false));
  }, [token, loading, router]);

  const hasElectionsTemplate = surveys.some(
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
        err instanceof Error ? err.message : "Waa lagu fashilmay ku darista qaabka doorashada"
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
          : "Waa lagu fashilmay ku darista qaabka fiisaha qaxootiga"
      );
    } finally {
      setAddingRefugeeKey(null);
    }
  }

  if (loading || busy) {
    return <p style={{ color: "var(--muted)" }}>Sahannada waa la soo rarayaa…</p>;
  }

  const missingRefugee = REFUGEE_TEMPLATES.filter(
    (t) => !surveys.some((s) => s.title === t.title)
  );

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
            Sahannadaada
          </h1>
          <p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
            Akoonnada cusub waxay helayaan qaababka shaqada, doorashada, iyo fiisaha
            qaxootiga (Kanada, Jarmalka, UK, Australia) — wax ka beddel, daabac, oo wadaag.
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
              {addingElections ? "Waa lagu darayaa…" : "Ku dar qaabka Kenya Elections"}
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
                ? "Waa lagu darayaa…"
                : `Ku dar fiisaha qaxootiga (${t.label})`}
            </button>
          ))}
          <Link href="/surveys/new" style={primaryLink}>
            Sahan cusub
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
          Weli ma jiraan sahanno. Samee mid si aad u hesho xiriiriye la wadaagi karo.
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
                    {DEFAULT_TEMPLATE_TITLES.has(s.title) ? "Qaabka caadiga ah · " : ""}
                    {s.question_count} su&apos;aalo · {s.response_count} jawaabo ·{" "}
                    <span style={{ color: s.status === "published" ? "var(--accent)" : "var(--warn)" }}>
                      {statusLabel(s.status)}
                    </span>
                  </p>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <Link href={`/surveys/${s.id}/edit`} style={chip}>
                    Wax ka beddel
                  </Link>
                  <Link href={`/surveys/${s.id}/results`} style={chip}>
                    Natiijooyinka
                  </Link>
                  {s.status === "published" && (
                    <Link href={`/s/${s.public_id}`} style={chip} target="_blank">
                      Fur xiriiriyaha
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
