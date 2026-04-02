"use client";

import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import type { PersonaType } from "@/data/personas";
import { PersonaResultCard } from "@/components/onboarding/persona-result-card";

export default function QuizResultPage() {
  const router = useRouter();
  const [personaType, setPersonaType] = useState<PersonaType | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("persona_type") as PersonaType | null;
    if (!stored) {
      router.replace("/onboarding/quiz");
      return;
    }
    setPersonaType(stored);
  }, [router]);

  if (!personaType) return null;

  function handleRetry() {
    sessionStorage.removeItem("persona_type");
    router.push("/onboarding/quiz");
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-lg flex-col items-center justify-center px-4 py-12">
      <PersonaResultCard personaType={personaType} />

      <div className="mt-10 flex w-full flex-col gap-3">
        <button
          type="button"
          onClick={() => router.push("/onboarding/form")}
          className="w-full rounded-lg bg-primary py-3.5 font-serif text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          나에게 맞는 국가 찾으러 가기
        </button>
        <button
          type="button"
          onClick={handleRetry}
          className="w-full py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          처음부터 다시하기
        </button>
      </div>
    </div>
  );
}
