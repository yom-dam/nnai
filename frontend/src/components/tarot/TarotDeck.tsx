"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import TarotCard from "./TarotCard";
import type { CityData } from "./types";

interface TarotDeckProps {
  cardCount: number;
  revealedCities: CityData[] | null;
  onReveal: (indices: number[]) => Promise<void>;
  onSelectForReading: (cityIndex: number) => void;
  initialSelectedIndices?: number[];
}

const MAX_FLIP = 3;
const CARD_COUNT = 5;

// Fan spread positions
const FAN_ANGLES = [-16, -8, 0, 8, 16];
const FAN_X = [-120, -60, 0, 60, 120];
const FAN_Y = [16, 5, 0, 5, 16];

type DeckPhase = "pack" | "exploding" | "cards" | "revealed" | "reading";

export default function TarotDeck({
  cardCount,
  revealedCities,
  onReveal,
  onSelectForReading,
  initialSelectedIndices,
}: TarotDeckProps) {
  // If we already have revealed cities (restored from session), skip to reading phase
  const hasRestoredReveal = revealedCities !== null && (initialSelectedIndices?.length ?? 0) > 0;

  const [phase, setPhase] = useState<DeckPhase>(hasRestoredReveal ? "reading" : "pack");
  const [flippedIndices, setFlippedIndices] = useState<number[]>(hasRestoredReveal ? (initialSelectedIndices ?? []) : []);
  const [isLoading, setIsLoading] = useState(false);
  const [readingIndex, setReadingIndex] = useState<number | null>(null);
  const [particles, setParticles] = useState<{ id: number; x: number; y: number; angle: number }[]>([]);

  const count = Math.min(cardCount || CARD_COUNT, CARD_COUNT);
  const allFlipped = flippedIndices.length >= MAX_FLIP;

  // When 3 cards are flipped, call onReveal to get city data
  useEffect(() => {
    if (flippedIndices.length === MAX_FLIP && !revealedCities && !isLoading) {
      setIsLoading(true);
      onReveal(flippedIndices).then(() => {
        setPhase("revealed");
        setIsLoading(false);
      }).catch(() => {
        setIsLoading(false);
      });
    }
  }, [flippedIndices.length]);

  // Pack explosion → show cards
  function handlePackClick() {
    setPhase("exploding");

    // Generate particles
    const newParticles = Array.from({ length: 20 }, (_, i) => ({
      id: i,
      x: (Math.random() - 0.5) * 300,
      y: (Math.random() - 0.5) * 300,
      angle: Math.random() * 360,
    }));
    setParticles(newParticles);

    // After explosion, show cards
    setTimeout(() => {
      setPhase("cards");
      setParticles([]);
    }, 1200);
  }

  // Individual card flip (Hearthstone style)
  function handleCardClick(i: number) {
    if (phase === "reading" || phase === "revealed") {
      // Reading selection phase
      const pos = flippedIndices.indexOf(i);
      if (pos < 0) return; // locked card
      setReadingIndex(i);
      return;
    }

    if (phase !== "cards") return;
    if (flippedIndices.includes(i)) return; // already flipped
    if (allFlipped) return; // max reached

    setFlippedIndices((prev) => [...prev, i]);
  }

  function handleReadingClick() {
    if (readingIndex === null || !revealedCities) return;
    const pos = flippedIndices.indexOf(readingIndex);
    if (pos < 0) return;
    onSelectForReading(pos);
  }

  // Get city data for a flipped card
  function getCityForSlot(i: number): CityData | null {
    if (!revealedCities) return null;
    const pos = flippedIndices.indexOf(i);
    return pos >= 0 ? (revealedCities[pos] ?? null) : null;
  }

  // Score-based glow tier (like Hearthstone rarity)
  function getGlowTier(city: CityData | null): "legendary" | "epic" | "rare" | "common" {
    if (!city) return "common";
    const score = city.score ?? 0;
    if (score >= 8) return "legendary";
    if (score >= 6) return "epic";
    if (score >= 4) return "rare";
    return "common";
  }

  return (
    <div className="flex flex-col items-center gap-8">
      {/* Phase: Pack */}
      <AnimatePresence mode="wait">
        {phase === "pack" && (
          <motion.div
            key="pack"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.5 }}
            transition={{ duration: 0.3 }}
            className="cursor-pointer"
            onClick={handlePackClick}
          >
            <div
              className="flex flex-col items-center justify-center border-2 border-primary/50 bg-card hover:border-primary hover:shadow-[0_0_24px_8px] hover:shadow-primary/30 transition-all"
              style={{ width: 140, height: 200, borderRadius: 12 }}
            >
              <span className="text-5xl mb-2">✦</span>
              <span className="text-xs font-semibold text-primary">NNAI</span>
              <span className="text-[10px] text-muted-foreground mt-1">탭하여 열기</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase: Exploding — particles */}
      {phase === "exploding" && (
        <div className="relative" style={{ width: 300, height: 300 }}>
          {/* Central flash */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 0.8 }}
          >
            <div className="w-32 h-32 rounded-full bg-primary/40 blur-2xl" />
          </motion.div>

          {/* Particles */}
          {particles.map((p) => (
            <motion.div
              key={p.id}
              className="absolute w-2 h-2 rounded-full bg-primary"
              style={{ left: "50%", top: "50%" }}
              initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
              animate={{ x: p.x, y: p.y, opacity: 0, scale: 0 }}
              transition={{ duration: 0.8 + Math.random() * 0.4, ease: "easeOut" }}
            />
          ))}
        </div>
      )}

      {/* Phase: Cards / Revealed / Reading */}
      {(phase === "cards" || phase === "revealed" || phase === "reading") && (
        <>
          <div
            className="relative flex items-end justify-center"
            style={{ width: 420, height: 260 }}
          >
            {Array.from({ length: count }).map((_, i) => {
              const angle = FAN_ANGLES[i] ?? 0;
              const xOffset = FAN_X[i] ?? 0;
              const yOffset = FAN_Y[i] ?? 0;
              const isFlipped = flippedIndices.includes(i);
              const isLocked = allFlipped && !isFlipped;
              const city = getCityForSlot(i);
              const isReadingSelected = readingIndex === i;
              const tier = getGlowTier(city);

              return (
                <motion.div
                  key={i}
                  className="absolute"
                  style={{
                    bottom: yOffset,
                    left: `calc(50% + ${xOffset}px)`,
                    marginLeft: -60,
                    transformOrigin: "bottom center",
                    zIndex: isFlipped || isReadingSelected ? 10 : 5 - Math.abs(i - 2),
                  }}
                  initial={{ opacity: 0, scale: 0, rotate: 0 }}
                  animate={{
                    opacity: 1,
                    scale: isReadingSelected ? 1.15 : isFlipped ? 1.05 : 1,
                    rotate: angle,
                    y: isReadingSelected ? -16 : isFlipped ? -8 : 0,
                  }}
                  transition={{
                    delay: phase === "cards" && !hasRestoredReveal ? i * 0.12 : 0,
                    type: "spring",
                    stiffness: 300,
                    damping: 25,
                  }}
                  whileHover={!isLocked ? { scale: 1.08, y: -6 } : undefined}
                >
                  <TarotCard
                    city={city}
                    isSelected={isReadingSelected}
                    isLocked={isLocked}
                    isFlipped={isFlipped}
                    glowTier={isFlipped ? tier : undefined}
                    onClick={() => handleCardClick(i)}
                  />
                </motion.div>
              );
            })}
          </div>

          {/* Status + CTA */}
          <div className="text-center space-y-4">
            {phase === "cards" && !allFlipped && (
              <p className="text-sm text-muted-foreground">
                {isLoading
                  ? "카드를 분석하고 있어요..."
                  : `끌리는 카드를 탭하세요 (${MAX_FLIP - flippedIndices.length}장 남음)`}
              </p>
            )}

            {phase === "cards" && allFlipped && isLoading && (
              <p className="text-sm text-muted-foreground animate-pulse">
                도시 정보를 불러오고 있어요...
              </p>
            )}

            {(phase === "revealed" || phase === "reading") && (
              <>
                <p className="text-sm text-muted-foreground">
                  {readingIndex === null
                    ? "리딩받고 싶은 도시 카드를 선택하세요"
                    : `${revealedCities?.[flippedIndices.indexOf(readingIndex)]?.city_kr ?? ""} 리딩을 시작할게요`}
                </p>
                {readingIndex !== null && (
                  <button
                    type="button"
                    onClick={handleReadingClick}
                    className="px-8 py-3 text-sm font-semibold transition-all bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    리딩 받기
                  </button>
                )}
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
