"use client";

import { motion } from "framer-motion";
import { PERSONAS, type PersonaType } from "@/data/personas";

interface PersonaResultCardProps {
  personaType: PersonaType;
}

export function PersonaResultCard({ personaType }: PersonaResultCardProps) {
  const persona = PERSONAS[personaType];

  const sections = [
    { label: "이런 도시가 어울려요", content: persona.city },
    { label: "이렇게 일해요", content: persona.work },
    { label: "당신에게 중요한 건", content: persona.value },
    { label: "이런 순간이 행복해요", content: persona.moment },
  ].filter((s) => s.content && s.content !== "TBD");

  const fadeUp = (delay: number) => ({
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const, delay } },
  });

  return (
    <div className="flex flex-col items-center gap-8 text-center">
      <motion.div className="space-y-3" {...fadeUp(0)}>
        <p className="text-sm text-muted-foreground">
          당신은
        </p>
        <h1 className="font-serif text-3xl font-semibold text-primary">
          {persona.label}
        </h1>
        <p className="font-serif text-sm text-muted-foreground leading-relaxed">
          {persona.description}
        </p>
      </motion.div>

      <div className="w-full grid gap-3 sm:grid-cols-2">
        {sections.map((section, i) => (
          <motion.div
            key={section.label}
            {...fadeUp(0.3 + i * 0.3)}
            className="rounded-lg border border-border bg-card px-4 py-4 text-left"
          >
            <p className="text-sm font-medium text-primary mb-2">
              {section.label}
            </p>
            <p className="whitespace-pre-line font-serif text-sm text-foreground leading-relaxed">
              {section.content}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
