"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  api,
  type LocationStatus,
  type PublicSurvey,
  type Question,
} from "@/lib/api";

type GeoResult = {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  location_status: LocationStatus;
};

type Props = {
  survey: PublicSurvey;
  publicId: string;
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

function QuestionFields({
  questions,
  answers,
  setAnswers,
}: {
  questions: Required<Question>[];
  answers: Record<number, string>;
  setAnswers: React.Dispatch<React.SetStateAction<Record<number, string>>>;
}) {
  return (
    <>
      {questions.map((q) => (
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
              rows={3}
              className="respond-textarea"
              placeholder="Halkan ku qor jawaabtaada"
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
    </>
  );
}

export function RefugeeWizard({ survey, publicId }: Props) {
  const sections = survey.sections?.length
    ? survey.sections
    : [{ id: "all", title: "Foomka", question_ids: survey.questions.map((q) => q.id) }];

  const questionsById = useMemo(() => {
    const map = new Map<number, Required<Question>>();
    survey.questions.forEach((q) => map.set(q.id, q));
    return map;
  }, [survey.questions]);

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>(() => {
    const initial: Record<number, string> = {};
    survey.questions.forEach((q) => {
      initial[q.id] = "";
    });
    return initial;
  });
  const [location, setLocation] = useState<GeoResult | null>(null);
  const [locating, setLocating] = useState(false);
  const [responseId, setResponseId] = useState<number | null>(null);
  const [editToken, setEditToken] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [savedFlash, setSavedFlash] = useState(false);

  const current = sections[step];
  const currentQuestions = current.question_ids
    .map((id) => questionsById.get(id))
    .filter((q): q is Required<Question> => Boolean(q));
  const isFirst = step === 0;
  const isLast = step === sections.length - 1;
  const locationReady = location?.location_status === "granted";
  const needsLocation = survey.collect_location;

  function validateSection(): string | null {
    for (const q of currentQuestions) {
      if (q.required && !(answers[q.id] || "").trim()) {
        return `Fadlan ka jawaab: ${q.prompt}`;
      }
    }
    if (isFirst && needsLocation && !locationReady) {
      return "Marka hore daar goobta ka hor intaadan gudbin tallaabadan.";
    }
    return null;
  }

  async function enableLocation() {
    setLocating(true);
    setError("");
    const geo = await captureLocation();
    setLocation(geo);
    setLocating(false);
    if (geo.location_status !== "granted") {
      setError(
        geo.location_status === "denied"
          ? "Oggolaanshaha goobta waa la diiday. Daar goobta goobaha browser-kaaga, ka dib isku day mar kale."
          : "Goobta lagama heli karo qalabkan. Daar GPS-ka oo isku day mar kale."
      );
    }
  }

  function flashSaved() {
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 1800);
  }

  async function onContinue(e: FormEvent) {
    e.preventDefault();
    const validation = validateSection();
    if (validation) {
      setError(validation);
      return;
    }

    setBusy(true);
    setError("");
    const sectionAnswers = currentQuestions.map((q) => ({
      question_id: q.id,
      value: answers[q.id] || "",
    }));

    try {
      if (isFirst) {
        const started = await api.startWizardResponse(publicId, {
          answers: sectionAnswers,
          latitude: location?.latitude,
          longitude: location?.longitude,
          accuracy: location?.accuracy,
          location_status: location?.location_status || "skipped",
        });
        setResponseId(started.response_id);
        setEditToken(started.edit_token);
        flashSaved();
        setStep(1);
      } else if (responseId != null && editToken) {
        await api.saveWizardStep(publicId, responseId, {
          edit_token: editToken,
          answers: sectionAnswers,
        });
        flashSaved();
        if (isLast) {
          await api.completeWizardResponse(publicId, responseId, {
            edit_token: editToken,
          });
          setDone(true);
        } else {
          setStep((s) => s + 1);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kaydintu way fashilantay");
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <section className="respond-page">
        <div
          className="respond-card"
          style={{ textAlign: "center", paddingTop: "2.5rem", paddingBottom: "2.5rem" }}
        >
          <h1 className="respond-success-title">
            Waad ku mahadsan tahay ka qaybqaadashada sahankan
          </h1>
          <p className="respond-success-text">
            Macluumaadkaaga waa la kaydiyay. Kooxdeenu way kula soo xiriiri doontaa.
          </p>
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

        <div className="wizard-progress" aria-label="Horumarka foomka">
          {sections.map((s, i) => (
            <div
              key={s.id}
              className={`wizard-progress-step${i === step ? " is-active" : ""}${
                i < step ? " is-done" : ""
              }`}
            >
              <span className="wizard-progress-dot">{i + 1}</span>
              <span className="wizard-progress-label">{s.title.replace(/^\d+\.\s*/, "")}</span>
            </div>
          ))}
        </div>

        <form onSubmit={onContinue} className="respond-form">
          <div className="respond-step is-ready">
            <strong className="respond-step-title">{current.title}</strong>
            <p className="respond-step-help" style={{ margin: "0.35rem 0 0" }}>
              Tallaabada {step + 1} ee {sections.length}
              {savedFlash ? " · Waa la kaydiyay" : ""}
            </p>
          </div>

          {isFirst && needsLocation && (
            <div className={`respond-step${locationReady ? " is-ready" : ""}`}>
              <strong className="respond-step-title">Goobta (laga bilaabo halkan)</strong>
              <p className="respond-step-help" style={{ margin: 0 }}>
                Goobta waa in la kaydiyaa marka tallaabada koowaad la gudbiyo.
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
                  Goobta waa la daaray
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
                  {locating ? "Goobta waa la helayaa…" : "Daar goobta"}
                </button>
              )}
            </div>
          )}

          <QuestionFields
            questions={currentQuestions}
            answers={answers}
            setAnswers={setAnswers}
          />

          {error && <p className="respond-error">{error}</p>}

          <div className="wizard-actions">
            {step > 0 && (
              <button
                type="button"
                className="respond-btn"
                disabled={busy}
                onClick={() => {
                  setError("");
                  setStep((s) => Math.max(0, s - 1));
                }}
                style={{
                  background: "transparent",
                  border: "1.5px solid var(--respond-line)",
                  color: "var(--respond-ink)",
                }}
              >
                Dib u noqo
              </button>
            )}
            <button
              type="submit"
              className="respond-btn respond-btn-primary"
              disabled={busy || (isFirst && needsLocation && !locationReady)}
            >
              {busy
                ? "Waa la kaydinayaa…"
                : isLast
                  ? "Dhammee oo gudbi"
                  : "Kaydi oo sii soco"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
