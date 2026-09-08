"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ResponseMap } from "@/components/ResponseMap";
import { api, TOKEN_KEY, type SurveyResults } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function ResultsPage() {
  const params = useParams();
  const surveyId = Number(params.id);
  const { token, loading } = useAuth();
  const router = useRouter();
  const [results, setResults] = useState<SurveyResults | null>(null);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.replace("/login");
      return;
    }
    api
      .getResults(token, surveyId)
      .then((data) => {
        setResults(data);
        if (data.responses.length) setSelectedId(data.responses[0].id);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load results"));
  }, [token, loading, router, surveyId]);

  const mapPoints = useMemo(() => {
    if (!results) return [];
    return results.responses
      .filter((r) => r.latitude != null && r.longitude != null)
      .map((r) => ({
        id: r.id,
        lat: r.latitude as number,
        lng: r.longitude as number,
        label: `#${r.id} · ${new Date(r.submitted_at).toLocaleString()}`,
      }));
  }, [results]);

  async function downloadCsv() {
    if (!token) return;
    const res = await fetch(api.exportCsvUrl(surveyId), {
      headers: { Authorization: `Bearer ${token || localStorage.getItem(TOKEN_KEY)}` },
    });
    if (!res.ok) {
      setError("CSV export failed");
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `survey-${surveyId}-results.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!results && !error) {
    return <p style={{ color: "var(--muted)" }}>Loading results…</p>;
  }

  if (error && !results) {
    return <p style={{ color: "var(--danger)" }}>{error}</p>;
  }

  if (!results) return null;

  const selected = results.responses.find((r) => r.id === selectedId) || null;
  const withLocation = mapPoints.length;

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "2rem" }}>
            {results.survey.title}
          </h1>
          <p style={{ margin: "0.35rem 0 0", color: "var(--muted)" }}>
            {results.total} responses · {withLocation} with location
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <Link href={`/surveys/${surveyId}/edit`} style={chip}>
            Edit
          </Link>
          <button type="button" onClick={downloadCsv} style={chipBtn}>
            Export CSV
          </button>
        </div>
      </div>

      <section style={{ display: "grid", gap: "0.75rem" }}>
        <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "1.25rem" }}>
          Response map
        </h2>
        <ResponseMap points={mapPoints} />
      </section>

      <section className="results-split">
        <div style={{ display: "grid", gap: "0.5rem", alignContent: "start" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "1.25rem" }}>
            Responses
          </h2>
          {results.responses.length === 0 && (
            <p style={{ color: "var(--muted)" }}>No responses yet.</p>
          )}
          {results.responses.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => setSelectedId(r.id)}
              style={{
                textAlign: "left",
                borderRadius: 12,
                border: `1px solid ${selectedId === r.id ? "var(--accent)" : "var(--line)"}`,
                background: selectedId === r.id ? "rgba(45,212,168,0.1)" : "var(--bg-card)",
                color: "var(--ink)",
                padding: "0.75rem 0.85rem",
                cursor: "pointer",
              }}
            >
              <div style={{ fontWeight: 600 }}>Response #{r.id}</div>
              <div style={{ color: "var(--muted)", fontSize: "0.85rem", marginTop: 2 }}>
                {new Date(r.submitted_at).toLocaleString()}
              </div>
              <div style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
                Location: {r.location_status}
                {r.latitude != null && r.longitude != null
                  ? ` (${r.latitude.toFixed(4)}, ${r.longitude.toFixed(4)})`
                  : ""}
              </div>
            </button>
          ))}
        </div>

        <div
          style={{
            border: "1px solid var(--line)",
            borderRadius: 14,
            padding: "1rem",
            background: "var(--bg-card)",
            minHeight: 240,
          }}
        >
          {!selected ? (
            <p style={{ color: "var(--muted)" }}>Select a response to inspect answers.</p>
          ) : (
            <div style={{ display: "grid", gap: "0.85rem" }}>
              <h3 style={{ margin: 0 }}>Response #{selected.id}</h3>
              <p style={{ margin: 0, color: "var(--muted)", fontSize: "0.92rem" }}>
                Submitted {new Date(selected.submitted_at).toLocaleString()}
                {selected.latitude != null && selected.longitude != null && (
                  <>
                    {" "}
                    · {selected.latitude.toFixed(5)}, {selected.longitude.toFixed(5)}
                    {selected.accuracy != null ? ` (±${Math.round(selected.accuracy)}m)` : ""}
                  </>
                )}
              </p>
              {selected.answers.map((a) => (
                <div key={a.question_id}>
                  <div style={{ color: "var(--muted)", fontSize: "0.85rem" }}>{a.prompt}</div>
                  <div style={{ marginTop: 2, fontWeight: 600 }}>{a.value || "—"}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      </div>
  );
}

const chip: React.CSSProperties = {
  border: "1px solid var(--line)",
  borderRadius: 999,
  padding: "0.45rem 0.9rem",
  fontSize: "0.9rem",
  alignSelf: "start",
};

const chipBtn: React.CSSProperties = {
  ...chip,
  background: "var(--accent)",
  color: "#06261d",
  border: "none",
  fontWeight: 700,
  cursor: "pointer",
};
