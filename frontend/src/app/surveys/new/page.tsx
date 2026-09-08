"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SurveyEditor } from "@/components/SurveyEditor";
import { api, type Question } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function NewSurveyPage() {
  const { token, loading } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [collectLocation, setCollectLocation] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([
    {
      prompt: "",
      question_type: "text",
      options: [],
      required: true,
      position: 0,
    },
  ]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && !token) router.replace("/login");
  }, [loading, token, router]);

  async function save(publish: boolean) {
    if (!token) return;
    if (!title.trim()) {
      setError("Cinwaanku waa waajib");
      return;
    }
    if (questions.some((q) => !q.prompt.trim())) {
      setError("Su'aal kasta waxay u baahan tahay qoraal");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const survey = await api.createSurvey(token, {
        title: title.trim(),
        description: description.trim(),
        collect_location: collectLocation,
        questions: questions.map((q, i) => ({ ...q, position: i })),
      });
      if (publish) {
        await api.updateSurvey(token, survey.id, { status: "published" });
      }
      router.push(`/surveys/${survey.id}/edit`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sahanka lama kaydin karin");
    } finally {
      setBusy(false);
    }
  }

  if (loading || !token) {
    return <p style={{ color: "var(--muted)" }}>Waa la soo rarayaa…</p>;
  }

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
        Sahan cusub
      </h1>
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
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <button type="button" disabled={busy} onClick={() => save(false)} style={secondary}>
          Kaydi qabyo
        </button>
        <button type="button" disabled={busy} onClick={() => save(true)} style={primary}>
          Kaydi oo daabac
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
