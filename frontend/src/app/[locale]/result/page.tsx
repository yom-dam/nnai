"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "@/i18n/navigation";
import TarotDeck from "@/components/tarot/TarotDeck";
import TarotReading from "@/components/tarot/TarotReading";
import CityCompare from "@/components/tarot/CityCompare";
import type { CityData, TarotStage, TarotSession } from "@/components/tarot/types";
import { TAROT_SESSION_KEY } from "@/components/tarot/types";

// ── Constants ──────────────────────────────────────────────────────

const RECOMMEND_PAYLOAD_KEY = "recommend_payload";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.nnai.app";

// ── Result Page ────────────────────────────────────────────────────

export default function ResultPage() {
  const router = useRouter();

  const [stage, setStage] = useState<TarotStage>("loading");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<Record<string, unknown> | null>(null);
  const [revealedCities, setRevealedCities] = useState<CityData[] | null>(null);
  const [savedSelectedIndices, setSavedSelectedIndices] = useState<number[]>([]);
  const [readingCityIndex, setReadingCityIndex] = useState<number | null>(null);
  const [readingMarkdown, setReadingMarkdown] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Save session to localStorage on stage changes
  const saveSession = useCallback(
    (
      overrides: Partial<TarotSession> & { stage: TarotStage }
    ) => {
      if (!sessionId && !overrides.session_id) return;
      const session: TarotSession = {
        session_id: overrides.session_id ?? sessionId ?? "",
        selectedIndices: overrides.selectedIndices ?? [],
        revealedCities: overrides.revealedCities ?? revealedCities ?? [],
        readingCityIndex: overrides.readingCityIndex ?? readingCityIndex ?? null,
        readingMarkdown: overrides.readingMarkdown ?? readingMarkdown ?? null,
        stage: overrides.stage,
      };
      localStorage.setItem(TAROT_SESSION_KEY, JSON.stringify(session));
    },
    [sessionId, revealedCities, readingCityIndex, readingMarkdown]
  );

  // Call /api/recommend using the payload stored in localStorage
  const startRecommend = useCallback(async () => {
    const payloadStr = localStorage.getItem(RECOMMEND_PAYLOAD_KEY);
    if (!payloadStr) {
      router.replace("/onboarding/form");
      return;
    }

    setStage("loading");
    setError(null);

    try {
      const payload = JSON.parse(payloadStr) as Record<string, unknown>;
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`recommend error: ${res.status}`);
      const data = await res.json() as {
        session_id: string;
        parsed: Record<string, unknown>;
      };

      setSessionId(data.session_id);
      setParsedData(data.parsed);

      const newStage: TarotStage = "deck";
      setStage(newStage);

      // Save initial session
      const session: TarotSession = {
        session_id: data.session_id,
        selectedIndices: [],
        revealedCities: [],
        readingCityIndex: null,
        readingMarkdown: null,
        stage: newStage,
      };
      localStorage.setItem(TAROT_SESSION_KEY, JSON.stringify(session));
    } catch {
      setError("추천을 불러오지 못했어요. 다시 시도해주세요.");
      setStage("error" as TarotStage);
    }
  }, [router]);

  // On mount: restore saved session or start fresh
  useEffect(() => {
    const savedStr = localStorage.getItem(TAROT_SESSION_KEY);
    if (savedStr) {
      try {
        const saved = JSON.parse(savedStr) as TarotSession;
        // Restore state
        setSessionId(saved.session_id);
        setRevealedCities(saved.revealedCities?.length ? saved.revealedCities : null);
        setSavedSelectedIndices(saved.selectedIndices ?? []);
        setReadingCityIndex(saved.readingCityIndex);
        setReadingMarkdown(saved.readingMarkdown);

        // Determine the right stage to resume
        let resumeStage = saved.stage;
        // If we were in reading but have no markdown yet, go back to revealed
        if (resumeStage === "reading" && !saved.readingMarkdown) {
          resumeStage = "revealed";
        }
        setStage(resumeStage);
        return;
      } catch {
        localStorage.removeItem(TAROT_SESSION_KEY);
      }
    }

    // No saved session — check for payload and start
    const hasPayload = !!localStorage.getItem(RECOMMEND_PAYLOAD_KEY);
    if (!hasPayload) {
      router.replace("/onboarding/form");
      return;
    }

    startRecommend();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Called by TarotDeck when user clicks "카드 열기"
  async function handleReveal(indices: number[]) {
    if (!sessionId) return;
    setError(null);

    try {
      const res = await fetch("/api/reveal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, selected_indices: indices }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({})) as { error?: string };
        throw new Error(errData.error ?? `reveal error: ${res.status}`);
      }
      const data = await res.json() as { revealed_cities: CityData[] };

      setRevealedCities(data.revealed_cities);
      const newStage: TarotStage = "revealed";
      setStage(newStage);
      saveSession({
        session_id: sessionId,
        selectedIndices: indices,
        revealedCities: data.revealed_cities,
        readingCityIndex: null,
        readingMarkdown: null,
        stage: newStage,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "카드 열기에 실패했어요.";
      setError(msg);
      throw err; // re-throw so TarotDeck can reset its loading state
    }
  }

  // Called by TarotDeck when user clicks "리딩 받기"
  async function handleSelectForReading(cityIndex: number) {
    if (!revealedCities || !parsedData) return;
    setError(null);

    // Check auth before proceeding
    try {
      const meRes = await fetch(`${API_URL}/auth/me`, { credentials: "include" });
      if (!meRes.ok) {
        // Not logged in — save state and redirect to OAuth
        const preOauthSession: TarotSession = {
          session_id: sessionId ?? "",
          selectedIndices: [],
          revealedCities: revealedCities,
          readingCityIndex: cityIndex,
          readingMarkdown: null,
          stage: "revealed",
        };
        localStorage.setItem(TAROT_SESSION_KEY, JSON.stringify(preOauthSession));
        window.location.href = `${API_URL}/auth/google`;
        return;
      }
    } catch {
      // Network error — treat as not logged in
      const preOauthSession: TarotSession = {
        session_id: sessionId ?? "",
        selectedIndices: [],
        revealedCities: revealedCities,
        readingCityIndex: cityIndex,
        readingMarkdown: null,
        stage: "revealed",
      };
      localStorage.setItem(TAROT_SESSION_KEY, JSON.stringify(preOauthSession));
      window.location.href = `${API_URL}/auth/google`;
      return;
    }

    // Logged in — fetch detail
    setReadingCityIndex(cityIndex);
    setStage("reading");
    saveSession({
      session_id: sessionId ?? "",
      selectedIndices: [],
      revealedCities: revealedCities,
      readingCityIndex: cityIndex,
      readingMarkdown: null,
      stage: "reading",
    });

    try {
      const res = await fetch("/api/detail", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ parsed_data: parsedData, city_index: cityIndex }),
      });
      if (!res.ok) throw new Error(`detail error: ${res.status}`);
      const data = await res.json() as { markdown: string };

      setReadingMarkdown(data.markdown);
      saveSession({
        session_id: sessionId ?? "",
        selectedIndices: [],
        revealedCities: revealedCities,
        readingCityIndex: cityIndex,
        readingMarkdown: data.markdown,
        stage: "reading",
      });
    } catch {
      setError("리딩을 불러오지 못했어요. 다시 시도해주세요.");
      setStage("revealed");
    }
  }

  function handleCompare() {
    const newStage: TarotStage = "comparing";
    setStage(newStage);
    saveSession({
      session_id: sessionId ?? "",
      selectedIndices: [],
      revealedCities: revealedCities ?? [],
      readingCityIndex,
      readingMarkdown,
      stage: newStage,
    });
  }

  function handleRetry() {
    localStorage.removeItem(TAROT_SESSION_KEY);
    localStorage.removeItem(RECOMMEND_PAYLOAD_KEY);
    localStorage.removeItem("persona_type");
    router.push("/onboarding/quiz");
  }

  // ── Render ──────────────────────────────────────────────────────

  if (stage === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="animate-pulse text-sm text-muted-foreground">
          당신의 카드를 준비하고 있어요...
        </p>
      </div>
    );
  }

  if ((stage as string) === "error") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4">
        <p className="text-sm text-destructive">{error ?? "오류가 발생했어요."}</p>
        <button
          type="button"
          onClick={() => startRecommend()}
          className="px-6 py-2 text-sm font-medium bg-primary text-primary-foreground rounded"
        >
          다시 시도
        </button>
        <button
          type="button"
          onClick={handleRetry}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          처음부터 다시하기
        </button>
      </div>
    );
  }

  if (stage === "deck" || stage === "selecting" || stage === "revealed") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
        <div className="mb-10 text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">
            당신의 카드를 선택하세요
          </h1>
          <p className="text-sm text-muted-foreground">
            {revealedCities
              ? "리딩받고 싶은 도시 카드를 선택하세요"
              : "5장의 카드 중 3장을 골라보세요"}
          </p>
        </div>

        {error && (
          <p className="mb-4 text-sm text-destructive text-center">{error}</p>
        )}

        <TarotDeck
          cardCount={5}
          revealedCities={revealedCities}
          onReveal={handleReveal}
          onSelectForReading={handleSelectForReading}
          initialSelectedIndices={savedSelectedIndices}
        />

        <button
          type="button"
          onClick={handleRetry}
          className="mt-12 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          처음부터 다시하기
        </button>
      </div>
    );
  }

  if (stage === "reading") {
    const city =
      readingCityIndex !== null && revealedCities
        ? revealedCities[readingCityIndex]
        : null;

    if (!city) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <p className="animate-pulse text-sm text-muted-foreground">
            리딩을 준비하고 있어요...
          </p>
        </div>
      );
    }

    if (!readingMarkdown) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <p className="animate-pulse text-sm text-muted-foreground">
            {city.city_kr} 리딩을 불러오는 중이에요...
          </p>
        </div>
      );
    }

    return (
      <TarotReading
        city={city}
        markdown={readingMarkdown}
        onCompare={handleCompare}
      />
    );
  }

  if (stage === "comparing") {
    return (
      <CityCompare
        cities={revealedCities ?? []}
        onRetry={handleRetry}
      />
    );
  }

  return null;
}
