import type { PersonaType } from "./personas";

export const QUIZ_QUESTION_COUNT = 7;

export const QUIZ_ANSWER_VALUES = ["A", "B", "C", "D"] as const;

export function calculatePersona(answers: string[]): PersonaType {
  const scores: Record<PersonaType, number> = {
    schengen_loop: 0,
    slow_nomad: 0,
    fire_optimizer: 0,
    burnout_escape: 0,
    expat_freedom: 0,
  };

  const ANSWER_MAP: Record<string, PersonaType> = {
    A: "schengen_loop",
    B: "slow_nomad",
    C: "fire_optimizer",
    D: "burnout_escape",
  };

  for (const answer of answers) {
    const persona = ANSWER_MAP[answer];
    if (persona) scores[persona]++;
  }

  if (answers[6] === "B") scores.expat_freedom += 2;

  return Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0] as PersonaType;
}
