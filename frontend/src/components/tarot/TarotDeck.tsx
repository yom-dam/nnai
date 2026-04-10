"use client";

import { motion, AnimatePresence } from "framer-motion";
import TarotCard from "./TarotCard";
import type { CityData } from "./types";

interface TarotDeckProps {
  cities: CityData[];
  selectedIndices: number[];
  revealedCities: CityData[] | null;
  onToggleSelect: (index: number) => void;
  onConfirm: () => void;
  isLoading: boolean;
}

const MAX_SELECT = 3;

export default function TarotDeck({
  cities,
  selectedIndices,
  revealedCities,
  onToggleSelect,
  onConfirm,
  isLoading,
}: TarotDeckProps) {
  const isRevealed = revealedCities !== null;
  const count = cities.length;
  const allSelected = selectedIndices.length === MAX_SELECT;

  function getCardState(i: number): "back" | "front" | "locked" {
    if (!isRevealed) return "back";
    return selectedIndices.includes(i) ? "front" : "locked";
  }

  function getCityForCard(i: number): CityData | null {
    if (!isRevealed) return cities[i] ?? null;
    const pos = selectedIndices.indexOf(i);
    return pos >= 0 ? (revealedCities[pos] ?? null) : (cities[i] ?? null);
  }

  return (
    <div className="flex flex-col items-center gap-8">
      {/* 5-card static row */}
      <div className="flex justify-center gap-4 flex-wrap">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="w-[160px]">
            <TarotCard
              state={getCardState(i)}
              cityData={getCityForCard(i)}
              isSelected={selectedIndices.includes(i)}
              onClick={() => {
                if (isLoading || isRevealed) return;
                onToggleSelect(i);
              }}
            />
          </div>
        ))}
      </div>

      {/* Status text */}
      <AnimatePresence mode="wait">
        {!isRevealed && (
          <motion.p
            key="select-hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-sm text-muted-foreground text-center"
          >
            {!allSelected
              ? `끌리는 카드 ${MAX_SELECT - selectedIndices.length}장을 골라보세요`
              : "준비되셨나요?"}
          </motion.p>
        )}
      </AnimatePresence>

      {/* Confirm CTA */}
      {!isRevealed && allSelected && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          type="button"
          onClick={onConfirm}
          disabled={isLoading}
          className="px-8 py-3 text-sm font-semibold bg-primary text-primary-foreground disabled:opacity-50 transition-opacity"
        >
          {isLoading ? "도시를 불러오고 있어요..." : "카드 열기"}
        </motion.button>
      )}
    </div>
  );
}
