"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";
import { ProgressBar } from "./progress-bar";

interface StepFormProps {
  currentStep: number;
  totalSteps: number;
  stepTitle: string;
  stepLabel: string;
  onNext: () => void;
  onBack: () => void;
  canProceed: boolean;
  children: ReactNode;
}

export function StepForm({
  currentStep,
  totalSteps,
  stepTitle,
  stepLabel,
  onNext,
  onBack,
  canProceed,
  children,
}: StepFormProps) {
  const t = useTranslations("common");
  const isLast = currentStep === totalSteps;
  const isFirst = currentStep === 1;

  return (
    <div className="flex min-h-dvh flex-col px-5 py-8">
      <div className="space-y-4">
        <ProgressBar
          current={currentStep}
          total={totalSteps}
          label={`Step ${currentStep}: ${stepLabel}`}
        />
        <h1 className="font-serif text-xl font-medium text-[var(--onboarding-text-primary)]">
          {stepTitle}
        </h1>
      </div>

      <div className="flex-1 py-8">{children}</div>

      <div className="flex gap-3 pb-4">
        {!isFirst && (
          <button
            type="button"
            onClick={onBack}
            className="flex-1 rounded-lg border border-[var(--onboarding-card-border)] py-3 font-serif text-sm text-[var(--onboarding-text-secondary)] transition-colors hover:border-[var(--onboarding-card-border-active)] hover:text-[var(--onboarding-text-primary)]"
          >
            {t("back")}
          </button>
        )}
        <button
          type="button"
          onClick={onNext}
          disabled={!canProceed}
          className="flex-1 rounded-lg border border-[var(--onboarding-accent)] bg-[var(--onboarding-accent-dim)] py-3 font-serif text-sm text-[var(--onboarding-accent)] transition-colors hover:bg-[var(--onboarding-accent)]/20 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {isLast ? t("startAnalysis") : t("next")}
        </button>
      </div>
    </div>
  );
}
