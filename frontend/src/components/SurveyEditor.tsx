"use client";

import { useState, type CSSProperties } from "react";
import type { Question, QuestionType } from "@/lib/api";

type Props = {
  title: string;
  description: string;
  collectLocation: boolean;
  questions: Question[];
  onChange: (next: {
    title: string;
    description: string;
    collectLocation: boolean;
    questions: Question[];
  }) => void;
};

const TYPES: { value: QuestionType; label: string }[] = [
  { value: "text", label: "Short text" },
  { value: "multiple_choice", label: "Multiple choice" },
  { value: "rating", label: "Rating 1–5" },
];

function blankQuestion(position: number): Question {
  return {
    prompt: "",
    question_type: "text",
    options: [],
    required: true,
    position,
  };
}

export function SurveyEditor({
  title,
  description,
  collectLocation,
  questions,
  onChange,
}: Props) {
  const [optionDrafts, setOptionDrafts] = useState<Record<number, string>>({});

  const update = (patch: Partial<Props>) => {
    onChange({
      title: patch.title ?? title,
      description: patch.description ?? description,
      collectLocation: patch.collectLocation ?? collectLocation,
      questions: patch.questions ?? questions,
    });
  };

  const setQuestion = (index: number, next: Question) => {
    const copy = [...questions];
    copy[index] = next;
    update({ questions: copy });
  };

  return (
    <div style={{ display: "grid", gap: "1.25rem" }}>
      <label style={labelStyle}>
        Survey title
        <input
          value={title}
          onChange={(e) => update({ title: e.target.value })}
          placeholder="e.g. Customer experience"
          style={inputStyle}
        />
      </label>
      <label style={labelStyle}>
        Description
        <textarea
          value={description}
          onChange={(e) => update({ description: e.target.value })}
          placeholder="Tell respondents what this survey is about"
          rows={3}
          style={{ ...inputStyle, resize: "vertical" }}
        />
      </label>
      <label
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: "0.75rem",
          padding: "1rem",
          borderRadius: 12,
          border: "1px solid var(--line)",
          background: "rgba(45, 212, 168, 0.06)",
        }}
      >
        <input
          type="checkbox"
          checked={collectLocation}
          onChange={(e) => update({ collectLocation: e.target.checked })}
          style={{ marginTop: 4 }}
        />
        <span>
          <strong style={{ display: "block", marginBottom: 4 }}>
            Collect location on submit
          </strong>
          <span style={{ color: "var(--muted)", fontSize: "0.92rem" }}>
            Respondents must enable GPS before they can submit.
            Submissions without location are rejected.
          </span>
        </span>
      </label>

      <div style={{ display: "grid", gap: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "1.35rem" }}>
            Questions
          </h2>
          <button
            type="button"
            onClick={() => update({ questions: [...questions, blankQuestion(questions.length)] })}
            style={secondaryBtn}
          >
            Add question
          </button>
        </div>

        {questions.length === 0 && (
          <p style={{ color: "var(--muted)" }}>
            Add at least one question before publishing.
          </p>
        )}

        {questions.map((q, index) => (
          <div
            key={index}
            style={{
              border: "1px solid var(--line)",
              borderRadius: 14,
              padding: "1rem",
              background: "var(--bg-card)",
              display: "grid",
              gap: "0.75rem",
            }}
          >
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <select
                value={q.question_type}
                onChange={(e) => {
                  const question_type = e.target.value as QuestionType;
                  setQuestion(index, {
                    ...q,
                    question_type,
                    options:
                      question_type === "rating"
                        ? ["1", "2", "3", "4", "5"]
                        : question_type === "multiple_choice"
                          ? q.options.length
                            ? q.options
                            : ["Option A", "Option B"]
                          : [],
                  });
                }}
                style={{ ...inputStyle, width: "auto", minWidth: 160 }}
              >
                {TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
              <label style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--muted)" }}>
                <input
                  type="checkbox"
                  checked={q.required}
                  onChange={(e) => setQuestion(index, { ...q, required: e.target.checked })}
                />
                Required
              </label>
              <button
                type="button"
                onClick={() =>
                  update({ questions: questions.filter((_, i) => i !== index) })
                }
                style={{
                  marginLeft: "auto",
                  background: "transparent",
                  border: "none",
                  color: "var(--danger)",
                  cursor: "pointer",
                }}
              >
                Delete
              </button>
            </div>
            <input
              value={q.prompt}
              onChange={(e) => setQuestion(index, { ...q, prompt: e.target.value })}
              placeholder={`Question ${index + 1}`}
              style={inputStyle}
            />
            {q.question_type === "multiple_choice" && (
              <div style={{ display: "grid", gap: "0.5rem" }}>
                {q.options.map((opt, oi) => (
                  <div key={oi} style={{ display: "flex", gap: "0.5rem" }}>
                    <input
                      value={opt}
                      onChange={(e) => {
                        const options = [...q.options];
                        options[oi] = e.target.value;
                        setQuestion(index, { ...q, options });
                      }}
                      style={inputStyle}
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setQuestion(index, {
                          ...q,
                          options: q.options.filter((_, i) => i !== oi),
                        })
                      }
                      style={{
                        background: "transparent",
                        border: "1px solid var(--line)",
                        color: "var(--muted)",
                        borderRadius: 8,
                        padding: "0 0.7rem",
                        cursor: "pointer",
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <input
                    value={optionDrafts[index] || ""}
                    onChange={(e) =>
                      setOptionDrafts((d) => ({ ...d, [index]: e.target.value }))
                    }
                    placeholder="New option"
                    style={inputStyle}
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const value = (optionDrafts[index] || "").trim();
                      if (!value) return;
                      setQuestion(index, { ...q, options: [...q.options, value] });
                      setOptionDrafts((d) => ({ ...d, [index]: "" }));
                    }}
                    style={secondaryBtn}
                  >
                    Add option
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const labelStyle: CSSProperties = {
  display: "grid",
  gap: "0.4rem",
  fontSize: "0.92rem",
  color: "var(--muted)",
};

const inputStyle: CSSProperties = {
  width: "100%",
  borderRadius: 10,
  border: "1px solid var(--line)",
  background: "rgba(0,0,0,0.25)",
  color: "var(--ink)",
  padding: "0.7rem 0.85rem",
};

const secondaryBtn: CSSProperties = {
  background: "transparent",
  border: "1px solid var(--line)",
  color: "var(--ink)",
  borderRadius: 999,
  padding: "0.45rem 0.95rem",
  cursor: "pointer",
  whiteSpace: "nowrap",
};
