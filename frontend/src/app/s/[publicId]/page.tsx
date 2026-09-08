"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { RefugeeWizard } from "@/components/RefugeeWizard";
import { api, type LocationStatus, type PublicSurvey } from "@/lib/api";

type GeoResult = {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  location_status: LocationStatus;
};

async function captureLocation(): Promise<GeoResult> {
  if (typeof navigator === "undefined" || !navigator.geolocation) {
    return {
      latitude: null,
      longitude: null,
      accuracy: null,
      location_status: "unavailable",
    };
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          location_status: "granted",
        });
      },
      (err) => {
        resolve({
          latitude: null,
          longitude: null,
          accuracy: null,
          location_status: err.code === err.PERMISSION_DENIED ? "denied" : "unavailable",
        });
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );
  });
}

export default function RespondPage() {
  const params = useParams();
  const publicId = String(params.publicId);
  const [survey, setSurvey] = useState<PublicSurvey | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [location, setLocation] = useState<GeoResult | null>(null);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  const needsLocation = Boolean(survey?.collect_location);
  const locationReady = location?.location_status === "granted";
  const canFillForm = !needsLocation || locationReady;

  useEffect(() => {
    api
      .getPublicSurvey(publicId)
      .then((s) => {
        setSurvey(s);
        const initial: Record<number, string> = {};
        s.questions.forEach((q) => {
          initial[q.id] = "";
        });
        setAnswers(initial);
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Survey not found")
      )
      .finally(() => setLoading(false));
  }, [publicId]);

  async function enableLocation() {
    setLocating(true);
    setError("");
    const geo = await captureLocation();
    setLocation(geo);
    setLocating(false);
    if (geo.location_status !== "granted") {
      setError(
        geo.location_status === "denied"
          ? "Location permission was denied. Enable location in your browser settings, then try again."
          : "Location is unavailable on this device. Enable GPS and try again."
      );
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!survey) return;

    if (needsLocation && !locationReady) {
      setError("Enable location first before filling out and submitting this form.");
      return;
    }

    for (const q of survey.questions) {
      if (q.required && !(answers[q.id] || "").trim()) {
        setError(`Please answer: ${q.prompt}`);
        return;
      }
    }

    setBusy(true);
    setError("");
    try {
      const geo: GeoResult = needsLocation
        ? location!
        : {
            latitude: null,
            longitude: null,
            accuracy: null,
            location_status: "skipped",
          };

      if (needsLocation && geo.location_status !== "granted") {
        setError("Location is required. Enable location first, then submit.");
        return;
      }

      await api.submitResponse(publicId, {
        answers: survey.questions.map((q) => ({
          question_id: q.id,
          value: answers[q.id] || "",
        })),
        ...geo,
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <section className="respond-page">
        <div className="respond-card">
          <p className="respond-hint" style={{ margin: 0, textAlign: "center" }}>
            Loading…
          </p>
        </div>
      </section>
    );
  }

  if (error && !survey) {
    return (
      <section className="respond-page">
        <div className="respond-card">
          <p className="respond-error" style={{ textAlign: "center" }}>
            {error}
          </p>
        </div>
      </section>
    );
  }

  if (!survey) return null;

  if (survey.wizard && survey.sections && survey.sections.length > 0) {
    return <RefugeeWizard survey={survey} publicId={publicId} />;
  }

  if (done) {
    return (
      <section className="respond-page">
        <div className="respond-card" style={{ textAlign: "center", paddingTop: "2.5rem", paddingBottom: "2.5rem" }}>
          <h1 className="respond-success-title">Thank you for taking this survey</h1>
          <p className="respond-success-text">Our team will be in touch.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="respond-page">
      <div className="respond-card">
        <p className="respond-brand">Maoni Yangu</p>
        <h1 className="respond-title">{survey.title}</h1>
        {survey.description && <p className="respond-desc">{survey.description}</p>}

        {needsLocation && (
          <div className={`respond-step${locationReady ? " is-ready" : ""}`}>
            <strong className="respond-step-title">Step 1 — Enable location</strong>
            <p className="respond-step-help" style={{ margin: 0 }}>
              Location must be enabled before you can answer and submit this survey.
            </p>
            {locationReady ? (
              <p
                style={{
                  margin: "0.75rem 0 0",
                  color: "var(--accent-deep)",
                  fontWeight: 700,
                  fontSize: "1.05rem",
                }}
              >
                Location enabled
                {location?.accuracy != null ? ` · ±${Math.round(location.accuracy)}m` : ""}
              </p>
            ) : (
              <button
                type="button"
                className="respond-btn respond-btn-primary"
                style={{ marginTop: "0.9rem" }}
                onClick={() => void enableLocation()}
                disabled={locating}
              >
                {locating ? "Getting location…" : "Enable location"}
              </button>
            )}
          </div>
        )}

        {!canFillForm ? (
          <p className="respond-hint" style={{ margin: "1.1rem 0 0" }}>
            Enable location above to unlock the survey form.
          </p>
        ) : (
          <form onSubmit={onSubmit} className="respond-form">
            {needsLocation && (
              <p className="respond-hint" style={{ margin: 0 }}>
                Step 2 — Answer the questions, then submit.
              </p>
            )}

            {survey.questions.map((q) => (
              <fieldset key={q.id} className="respond-question">
                <legend>
                  {q.prompt}
                  {q.required ? " *" : ""}
                </legend>

                {q.question_type === "text" && (
                  <textarea
                    required={q.required}
                    value={answers[q.id] || ""}
                    onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
                    rows={4}
                    className="respond-textarea"
                    placeholder="Type your answer here"
                  />
                )}

                {q.question_type === "multiple_choice" && (
                  <div className="respond-options">
                    {q.options.map((opt) => (
                      <label key={opt} className="respond-option">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          required={q.required}
                          checked={answers[q.id] === opt}
                          onChange={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                        />
                        <span>{opt}</span>
                      </label>
                    ))}
                  </div>
                )}

                {q.question_type === "rating" && (
                  <div className="respond-rating">
                    {(q.options.length ? q.options : ["1", "2", "3", "4", "5"]).map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        className={answers[q.id] === opt ? "is-selected" : undefined}
                        onClick={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}
              </fieldset>
            ))}

            {error && <p className="respond-error">{error}</p>}

            <button
              type="submit"
              className="respond-btn respond-btn-primary"
              disabled={busy || (needsLocation && !locationReady)}
            >
              {busy ? "Submitting…" : "Submit response"}
            </button>
          </form>
        )}

        {error && !canFillForm && <p className="respond-error" style={{ marginTop: "1rem" }}>{error}</p>}
      </div>
    </section>
  );
}
