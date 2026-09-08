"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthCard, Field, inputStyle, primaryBtn } from "@/components/AuthForm";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthCard title="Welcome back" subtitle="Log in to manage your surveys.">
      <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.9rem" }}>
        <Field label="Email or username">
          <input
            type="text"
            autoComplete="username"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
            placeholder="you@example.com or netizen"
          />
        </Field>
        <Field label="Password">
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={inputStyle}
          />
        </Field>
        {error && <p style={{ color: "var(--danger)", margin: 0 }}>{error}</p>}
        <button type="submit" disabled={busy} style={primaryBtn}>
          {busy ? "Signing in…" : "Log in"}
        </button>
      </form>
      <p style={{ color: "var(--muted)", marginTop: "1rem" }}>
        No account? <Link href="/register">Register</Link>
      </p>
    </AuthCard>
  );
}
