"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import type { PersonaType } from "@/data/personas";
import {
  NATIONALITY_VALUES,
  LANGUAGE_VALUES,
  PURPOSE_VALUES,
  TIMELINE_VALUES,
  LIFESTYLE_VALUES,
  TRAVEL_TYPE_VALUES,
  INCOME_TYPE_VALUES,
  PREFERRED_REGION_VALUES,
  READINESS_VALUES,
  SPOUSE_INCOME_VALUES,
} from "@/data/form-options";
import { StepForm } from "@/components/onboarding/step-form";
import { SelectCard } from "@/components/onboarding/select-card";

interface FormData {
  nationality: string;
  dual_nationality: boolean;
  languages: string[];
  immigration_purpose: string;
  timeline: string;
  lifestyle: string[];
  travel_type: string;
  children_ages: string[];
  has_spouse_income: string;
  spouse_income_krw: number;
  income_type: string;
  income_krw: number;
  preferred_countries: string[];
  readiness_stage: string;
}

const INITIAL_FORM: FormData = {
  nationality: "",
  dual_nationality: false,
  languages: [],
  immigration_purpose: "",
  timeline: "",
  lifestyle: [],
  travel_type: "",
  children_ages: [],
  has_spouse_income: "없음",
  spouse_income_krw: 0,
  income_type: "",
  income_krw: 0,
  preferred_countries: [],
  readiness_stage: "",
};

const TOTAL_STEPS = 6;

function hasChildren(travelType: string) {
  return travelType.includes("자녀");
}

function hasSpouse(travelType: string) {
  return travelType.includes("배우자") || travelType.includes("가족");
}

const INPUT_CLASS =
  "w-full rounded-lg border border-[var(--onboarding-card-border)] bg-[var(--onboarding-card-bg)] px-4 py-3 font-serif text-sm text-[var(--onboarding-text-primary)] placeholder:text-[var(--onboarding-text-secondary)]/40 focus:border-[var(--onboarding-card-border-active)] focus:outline-none";

function buildOptions(labels: string[], values: string[]) {
  return labels.map((label, i) => ({ label, value: values[i] }));
}

export default function FormPage() {
  const router = useRouter();
  const t = useTranslations("form");
  const pt = useTranslations("persona");
  const [personaType, setPersonaType] = useState<PersonaType | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [form, setForm] = useState<FormData>(INITIAL_FORM);

  useEffect(() => {
    const stored = sessionStorage.getItem("persona_type") as PersonaType | null;
    setPersonaType(stored);
  }, []);

  function canProceed(): boolean {
    switch (currentStep) {
      case 1: return form.nationality !== "" && form.languages.length > 0;
      case 2: return form.immigration_purpose !== "" && form.timeline !== "";
      case 3: return form.lifestyle.length > 0;
      case 4: return form.travel_type !== "";
      case 5: return form.income_type !== "" && form.income_krw > 0;
      case 6: return form.readiness_stage !== "";
      default: return false;
    }
  }

  function handleNext() {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1);
    } else {
      const payload = { ...form, persona_type: personaType ?? "" };
      console.log("[FormPage] Submit payload:", payload);
      router.push("/result");
    }
  }

  function handleBack() {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  }

  function toggleMulti(field: keyof FormData, value: string, max?: number) {
    setForm((prev) => {
      const arr = prev[field] as string[];
      if (arr.includes(value)) {
        return { ...prev, [field]: arr.filter((v) => v !== value) };
      }
      if (max && arr.length >= max) return prev;
      return { ...prev, [field]: [...arr, value] };
    });
  }

  function incomeLabel(): string {
    if (form.income_type.includes("프리랜서")) return t("labels.incomeFreelancer");
    if (form.income_type.includes("은퇴")) return t("labels.incomeRetired");
    return t("labels.incomeDefault");
  }

  const stepLabels = t.raw("stepLabels") as string[];
  const stepTitles = t.raw("stepTitles") as string[];

  return (
    <StepForm
      currentStep={currentStep}
      totalSteps={TOTAL_STEPS}
      stepTitle={stepTitles[currentStep - 1]}
      stepLabel={stepLabels[currentStep - 1]}
      onNext={handleNext}
      onBack={handleBack}
      canProceed={canProceed()}
    >
      {personaType && (
        <div className="mb-6 rounded-lg border border-[var(--onboarding-accent-dim)] bg-[var(--onboarding-accent-dim)] px-3 py-2 text-center font-serif text-xs text-[var(--onboarding-accent)]">
          {pt("analyzingAs", { label: pt(`types.${personaType}.label`) })}
        </div>
      )}

      {currentStep === 1 && (
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.nationality")}</label>
            <SelectCard options={buildOptions(t.raw("options.nationality") as string[], NATIONALITY_VALUES)} selected={form.nationality} onSelect={(v) => setForm({ ...form, nationality: v })} mode="single" />
          </div>
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.dualNationality")}</label>
            <button type="button" onClick={() => setForm({ ...form, dual_nationality: !form.dual_nationality })} className={`w-full rounded-lg border px-4 py-3 text-left font-serif text-sm transition-colors ${form.dual_nationality ? "border-[var(--onboarding-card-border-active)] bg-[var(--onboarding-card-bg-active)] text-[var(--onboarding-text-primary)]" : "border-[var(--onboarding-card-border)] bg-[var(--onboarding-card-bg)] text-[var(--onboarding-text-secondary)]"}`}>
              {form.dual_nationality ? t("labels.dualYes") : t("labels.dualNo")}
            </button>
          </div>
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.languages")}</label>
            <SelectCard options={buildOptions(t.raw("options.languages") as string[], LANGUAGE_VALUES)} selected={form.languages} onSelect={(v) => toggleMulti("languages", v)} mode="multi" />
          </div>
        </div>
      )}

      {currentStep === 2 && (
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.purpose")}</label>
            <SelectCard options={buildOptions(t.raw("options.purpose") as string[], PURPOSE_VALUES)} selected={form.immigration_purpose} onSelect={(v) => setForm({ ...form, immigration_purpose: v })} mode="single" />
          </div>
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.timeline")}</label>
            <SelectCard options={buildOptions(t.raw("options.timeline") as string[], TIMELINE_VALUES)} selected={form.timeline} onSelect={(v) => setForm({ ...form, timeline: v })} mode="single" />
          </div>
        </div>
      )}

      {currentStep === 3 && (
        <div className="space-y-2">
          <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.lifestyle")}</label>
          <SelectCard options={buildOptions(t.raw("options.lifestyle") as string[], LIFESTYLE_VALUES)} selected={form.lifestyle} onSelect={(v) => toggleMulti("lifestyle", v, 3)} mode="multi" maxSelect={3} />
        </div>
      )}

      {currentStep === 4 && (
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.travelType")}</label>
            <SelectCard options={buildOptions(t.raw("options.travelType") as string[], TRAVEL_TYPE_VALUES)} selected={form.travel_type} onSelect={(v) => setForm({ ...form, travel_type: v })} mode="single" />
          </div>
          {hasChildren(form.travel_type) && (
            <div className="space-y-2">
              <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.childrenAges")}</label>
              <input type="text" placeholder={t("labels.childrenPlaceholder")} value={form.children_ages.join(", ")} onChange={(e) => setForm({ ...form, children_ages: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })} className={INPUT_CLASS} />
            </div>
          )}
          {hasSpouse(form.travel_type) && (
            <>
              <div className="space-y-2">
                <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.spouseIncome")}</label>
                <SelectCard options={buildOptions(t.raw("options.spouseIncome") as string[], SPOUSE_INCOME_VALUES)} selected={form.has_spouse_income} onSelect={(v) => setForm({ ...form, has_spouse_income: v })} mode="single" />
              </div>
              {form.has_spouse_income === "있음" && (
                <div className="space-y-2">
                  <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.spouseIncomeAmount")}</label>
                  <input type="number" placeholder="0" value={form.spouse_income_krw || ""} onChange={(e) => setForm({ ...form, spouse_income_krw: Number(e.target.value) || 0 })} className={INPUT_CLASS} />
                </div>
              )}
            </>
          )}
        </div>
      )}

      {currentStep === 5 && (
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.incomeType")}</label>
            <SelectCard options={buildOptions(t.raw("options.incomeType") as string[], INCOME_TYPE_VALUES)} selected={form.income_type} onSelect={(v) => setForm({ ...form, income_type: v })} mode="single" />
          </div>
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{incomeLabel()}</label>
            <input type="number" placeholder="0" value={form.income_krw || ""} onChange={(e) => setForm({ ...form, income_krw: Number(e.target.value) || 0 })} className={INPUT_CLASS} />
          </div>
        </div>
      )}

      {currentStep === 6 && (
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.preferredRegion")}</label>
            <SelectCard options={buildOptions(t.raw("options.preferredRegion") as string[], PREFERRED_REGION_VALUES)} selected={form.preferred_countries} onSelect={(v) => toggleMulti("preferred_countries", v)} mode="multi" />
          </div>
          <div className="space-y-2">
            <label className="font-serif text-sm text-[var(--onboarding-text-secondary)]">{t("labels.readiness")}</label>
            <SelectCard options={buildOptions(t.raw("options.readiness") as string[], READINESS_VALUES)} selected={form.readiness_stage} onSelect={(v) => setForm({ ...form, readiness_stage: v })} mode="single" />
          </div>
        </div>
      )}
    </StepForm>
  );
}
