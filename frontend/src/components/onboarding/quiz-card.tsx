"use client";

interface QuizCardProps {
  question: string;
  options: string[];
  onSelect: (answerIndex: number) => void;
}

export function QuizCard({ question, options, onSelect }: QuizCardProps) {
  return (
    <div className="flex flex-col gap-6">
      <h2 className="font-serif text-xl font-medium leading-relaxed text-[var(--onboarding-text-primary)]">
        {question}
      </h2>
      <div className="grid gap-3">
        {options.map((option, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onSelect(i)}
            className="w-full rounded-lg border border-[var(--onboarding-card-border)] bg-[var(--onboarding-card-bg)] px-4 py-3.5 text-left font-serif text-sm text-[var(--onboarding-text-secondary)] transition-colors hover:border-[var(--onboarding-card-border-active)] hover:bg-[var(--onboarding-card-bg-active)] hover:text-[var(--onboarding-text-primary)]"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
