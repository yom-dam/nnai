"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { QUIZ_QUESTION_COUNT, QUIZ_ANSWER_VALUES, calculatePersona } from "@/data/quiz-questions";
import { QuizCard } from "@/components/onboarding/quiz-card";
import { ProgressBar } from "@/components/onboarding/progress-bar";

export default function QuizPage() {
  const router = useRouter();
  const t = useTranslations("quiz");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);

  function handleSelect(answerIndex: number) {
    const value = QUIZ_ANSWER_VALUES[answerIndex];
    const newAnswers = [...answers, value];
    setAnswers(newAnswers);

    if (currentIndex < QUIZ_QUESTION_COUNT - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      const persona = calculatePersona(newAnswers);
      sessionStorage.setItem("persona_type", persona);
      router.push("/onboarding/quiz/result");
    }
  }

  const question = t(`questions.${currentIndex}.question`);
  const options = t.raw(`questions.${currentIndex}.options`) as string[];

  return (
    <div className="flex min-h-dvh flex-col px-5 py-8">
      <ProgressBar current={currentIndex + 1} total={QUIZ_QUESTION_COUNT} />
      <div className="flex flex-1 items-center">
        <div className="w-full">
          <QuizCard question={question} options={options} onSelect={handleSelect} />
        </div>
      </div>
    </div>
  );
}
