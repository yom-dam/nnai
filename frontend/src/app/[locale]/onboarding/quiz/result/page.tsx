"use client";

import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import type { PersonaType } from "@/data/personas";
import { PersonaResultCard } from "@/components/onboarding/persona-result-card";

export default function QuizResultPage() {
  const router = useRouter();
  const [personaType] = useState<PersonaType | null>(() => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("persona_type") as PersonaType | null;
  });

  useEffect(() => {
    if (!personaType) {
      router.replace("/onboarding/quiz");
    }
  }, [personaType, router]);

  if (!personaType) return null;

  function handleRetry() {
    localStorage.removeItem("persona_type");
    router.push("/onboarding/quiz");
  }

  return (
    <PersonaResultCard
      personaType={personaType}
      onFindCountry={() => router.push("/onboarding/form")}
      onRetry={handleRetry}
    />
  );
}
