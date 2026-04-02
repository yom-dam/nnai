"use client";

interface QuizCardProps {
  question: string;
  options: string[];
  onSelect: (answerIndex: number) => void;
}

export function QuizCard({ question, options, onSelect }: QuizCardProps) {
  return (
    <div className="flex flex-col">
      <h2 className="whitespace-pre-line text-xl font-medium leading-relaxed text-foreground mb-8">
        {question}
      </h2>
      <div className="grid gap-3">
        {options.map((option, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onSelect(i)}
            className="w-full rounded-lg bg-muted px-4 py-4 text-left text-sm font-medium text-foreground transition-colors hover:bg-accent"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
