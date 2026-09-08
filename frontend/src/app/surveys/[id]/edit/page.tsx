"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { SurveyEditor } from "@/components/SurveyEditor";
import { api, type Question, type Survey } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function EditSurveyPage() {
  const params = useParams();
  const surveyId = Number(params.id);
  const { token, loading } = useAuth();
  const router = useRouter();
  const [survey, setSurvey] = useState<Survey | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [collectLocation, setCollectLocation] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.replace("/login");
      return;
    }
    api
      .getSurvey(token, surveyId)
      .then((s) => {
        setSurvey(s);
        setTitle(s.title);
        setDescription(s.description);
        setCollectLocation(s.collect_location);
        setQuestions(
          s.questions.map((q, i) => ({
            prompt: q.prompt,
            question_type: q.question_type,
            options: q.options || [],
            required: q.required,
            position: q.position ?? i,
          }))
        );
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Waa lagu fashilmay soo raridda")
      );
  }, [token, loading, router, surveyId]);

  async function save(extra?: { status?: "draft" | "published" }) {
    if (!token || !survey) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const updated = await api.updateSurvey(token, survey.id, {
        title: title.trim(),
        description: description.trim(),
        collect_location: collectLocation,
        questions: questions.map((q, i) => ({ ...q, position: i })),
        ...extra,
      });
      setSurvey(updated);
      setMessage(extra?.status === "published" ? "Waa la daabacay." : "Waa la kaydiyay.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kaydintu way fashilantay");
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!token || !survey) return;
    if (!confirm("Ma tirtiraysaa sahankan iyo dhammaan jawaabaha?")) return;
    await api.deleteSurvey(token, survey.id);
    router.push("/dashboard");
  }

  if (!survey && !error) {
    return <p style={{ color: "var(--muted)" }}>Sahanka waa la soo rarayaa…</p>;
  }

  if (error && !survey) {
    return <p style={{ color: "var(--danger)" }}>{error}</p>;
  }

  if (!survey) return null;

  const shareUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/s/${survey.public_id}`
      : `/s/${survey.public_id}`;

  const statusLabel = survey.status === "published" ? "la daabacay" : "qabyo";

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
            Wax ka beddel sahanka
          </h1>
          <p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
            Xaaladda:{" "}
            <span style={{ color: survey.status === "published" ? "var(--accent)" : "var(--warn)" }}>
              {statusLabel}
            </span>
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <Link href={`/surveys/${survey.id}/results`} style={chip}>
            Natiijooyinka
          </Link>
          {survey.status === "published" && (
            <Link href={`/s/${survey.public_id}`} style={chip} target="_blank">
              Horudhac
            </Link>
          )}
        </div>
      </div>

      {survey.status === "published" && (
        <div
          style={{
            padding: "0.9rem 1rem",
            borderRadius: 12,
            border: "1px solid var(--line)",
            background: "rgba(45,212,168,0.08)",
            display: "grid",
            gap: "0.4rem",
          }}
        >
          <strong>Xiriiriyaha wadaagista</strong>
          <code style={{ wordBreak: "break-all", color: "var(--accent)" }}>{shareUrl}</code>
          <button
            type="button"
            onClick={() => navigator.clipboard.writeText(shareUrl)}
            style={chipBtn}
          >
            Koobi garee xiriiriyaha
          </button>
        </div>
      )}

      <SurveyEditor
        title={title}
        description={description}
        collectLocation={collectLocation}
        questions={questions}
        onChange={({ title: t, description: d, collectLocation: c, questions: qs }) => {
          setTitle(t);
          setDescription(d);
          setCollectLocation(c);
          setQuestions(qs);
        }}
      />

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      {message && <p style={{ color: "var(--accent)" }}>{message}</p>}

      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <button type="button" disabled={busy} onClick={() => save()} style={secondary}>
          Kaydi isbeddelada
        </button>
        {survey.status !== "published" ? (
          <button
            type="button"
            disabled={busy}
            onClick={() => save({ status: "published" })}
            style={primary}
          >
            Daabac
          </button>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={() => save({ status: "draft" })}
            style={secondary}
          >
            Ka noqo daabacaadda
          </button>
        )}
        <button type="button" onClick={remove} style={{ ...secondary, color: "var(--danger)" }}>
          Tirtir
        </button>
      </div>
    </div>
  );
}

const primary: React.CSSProperties = {
  background: "var(--accent)",
  color: "#06261d",
  border: "none",
  borderRadius: 999,
  padding: "0.7rem 1.2rem",
  fontWeight: 700,
  cursor: "pointer",
};

const secondary: React.CSSProperties = {
  background: "transparent",
  color: "var(--ink)",
  border: "1px solid var(--line)",
  borderRadius: 999,
  padding: "0.7rem 1.2rem",
  cursor: "pointer",
};

const chip: React.CSSProperties = {
  border: "1px solid var(--line)",
  borderRadius: 999,
  padding: "0.4rem 0.85rem",
  fontSize: "0.9rem",
  alignSelf: "start",
};

const chipBtn: React.CSSProperties = {
  ...chip,
  background: "transparent",
  color: "var(--ink)",
  cursor: "pointer",
  width: "fit-content",
};
