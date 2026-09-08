"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthCard, Field, inputStyle, primaryBtn } from "@/components/AuthForm";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(name, email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Diiwaangelintu way fashilantay");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthCard
      title="Samee akoon"
      subtitle="Bilow sameynta sahanno goobtu ka muuqato."
    >
      <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.9rem" }}>
        <Field label="Magaca">
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={inputStyle}
          />
        </Field>
        <Field label="Iimayl">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
          />
        </Field>
        <Field label="Furaha sirta">
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={inputStyle}
          />
        </Field>
        {error && <p style={{ color: "var(--danger)", margin: 0 }}>{error}</p>}
        <button type="submit" disabled={busy} style={primaryBtn}>
          {busy ? "Waa la sameynayaa…" : "Samee akoon"}
        </button>
      </form>
      <p style={{ color: "var(--muted)", marginTop: "1rem" }}>
        Horay ma u leedahay akoon? <Link href="/login">Gal</Link>
      </p>
    </AuthCard>
  );
}
