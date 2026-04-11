"use client";

import { motion } from "framer-motion";
import type { CityData } from "./types";

// Flag emoji mapping by country_id (ISO-2)
const FLAG_EMOJI: Record<string, string> = {
  AD: "🇦🇩", AE: "🇦🇪", AF: "🇦🇫", AG: "🇦🇬", AL: "🇦🇱",
  AM: "🇦🇲", AO: "🇦🇴", AR: "🇦🇷", AT: "🇦🇹", AU: "🇦🇺",
  AZ: "🇦🇿", BA: "🇧🇦", BB: "🇧🇧", BD: "🇧🇩", BE: "🇧🇪",
  BF: "🇧🇫", BG: "🇧🇬", BH: "🇧🇭", BI: "🇧🇮", BJ: "🇧🇯",
  BN: "🇧🇳", BO: "🇧🇴", BR: "🇧🇷", BS: "🇧🇸", BT: "🇧🇹",
  BW: "🇧🇼", BY: "🇧🇾", BZ: "🇧🇿", CA: "🇨🇦", CD: "🇨🇩",
  CF: "🇨🇫", CG: "🇨🇬", CH: "🇨🇭", CI: "🇨🇮", CL: "🇨🇱",
  CM: "🇨🇲", CN: "🇨🇳", CO: "🇨🇴", CR: "🇨🇷", CU: "🇨🇺",
  CV: "🇨🇻", CY: "🇨🇾", CZ: "🇨🇿", DE: "🇩🇪", DJ: "🇩🇯",
  DK: "🇩🇰", DM: "🇩🇲", DO: "🇩🇴", DZ: "🇩🇿", EC: "🇪🇨",
  EE: "🇪🇪", EG: "🇪🇬", ER: "🇪🇷", ES: "🇪🇸", ET: "🇪🇹",
  FI: "🇫🇮", FJ: "🇫🇯", FM: "🇫🇲", FR: "🇫🇷", GA: "🇬🇦",
  GB: "🇬🇧", GD: "🇬🇩", GE: "🇬🇪", GH: "🇬🇭", GM: "🇬🇲",
  GN: "🇬🇳", GQ: "🇬🇶", GR: "🇬🇷", GT: "🇬🇹", GW: "🇬🇼",
  GY: "🇬🇾", HN: "🇭🇳", HR: "🇭🇷", HT: "🇭🇹", HU: "🇭🇺",
  ID: "🇮🇩", IE: "🇮🇪", IL: "🇮🇱", IN: "🇮🇳", IQ: "🇮🇶",
  IR: "🇮🇷", IS: "🇮🇸", IT: "🇮🇹", JM: "🇯🇲", JO: "🇯🇴",
  JP: "🇯🇵", KE: "🇰🇪", KG: "🇰🇬", KH: "🇰🇭", KI: "🇰🇮",
  KM: "🇰🇲", KN: "🇰🇳", KP: "🇰🇵", KR: "🇰🇷", KW: "🇰🇼",
  KZ: "🇰🇿", LA: "🇱🇦", LB: "🇱🇧", LC: "🇱🇨", LI: "🇱🇮",
  LK: "🇱🇰", LR: "🇱🇷", LS: "🇱🇸", LT: "🇱🇹", LU: "🇱🇺",
  LV: "🇱🇻", LY: "🇱🇾", MA: "🇲🇦", MC: "🇲🇨", MD: "🇲🇩",
  ME: "🇲🇪", MG: "🇲🇬", MH: "🇲🇭", MK: "🇲🇰", ML: "🇲🇱",
  MM: "🇲🇲", MN: "🇲🇳", MR: "🇲🇷", MT: "🇲🇹", MU: "🇲🇺",
  MV: "🇲🇻", MW: "🇲🇼", MX: "🇲🇽", MY: "🇲🇾", MZ: "🇲🇿",
  NA: "🇳🇦", NE: "🇳🇪", NG: "🇳🇬", NI: "🇳🇮", NL: "🇳🇱",
  NO: "🇳🇴", NP: "🇳🇵", NR: "🇳🇷", NZ: "🇳🇿", OM: "🇴🇲",
  PA: "🇵🇦", PE: "🇵🇪", PG: "🇵🇬", PH: "🇵🇭", PK: "🇵🇰",
  PL: "🇵🇱", PT: "🇵🇹", PW: "🇵🇼", PY: "🇵🇾", QA: "🇶🇦",
  RO: "🇷🇴", RS: "🇷🇸", RU: "🇷🇺", RW: "🇷🇼", SA: "🇸🇦",
  SB: "🇸🇧", SC: "🇸🇨", SD: "🇸🇩", SE: "🇸🇪", SG: "🇸🇬",
  SI: "🇸🇮", SK: "🇸🇰", SL: "🇸🇱", SM: "🇸🇲", SN: "🇸🇳",
  SO: "🇸🇴", SR: "🇸🇷", SS: "🇸🇸", ST: "🇸🇹", SV: "🇸🇻",
  SY: "🇸🇾", SZ: "🇸🇿", TD: "🇹🇩", TG: "🇹🇬", TH: "🇹🇭",
  TJ: "🇹🇯", TL: "🇹🇱", TM: "🇹🇲", TN: "🇹🇳", TO: "🇹🇴",
  TR: "🇹🇷", TT: "🇹🇹", TV: "🇹🇻", TZ: "🇹🇿", UA: "🇺🇦",
  UG: "🇺🇬", US: "🇺🇸", UY: "🇺🇾", UZ: "🇺🇿", VA: "🇻🇦",
  VC: "🇻🇨", VE: "🇻🇪", VN: "🇻🇳", VU: "🇻🇺", WS: "🇼🇸",
  YE: "🇾🇪", ZA: "🇿🇦", ZM: "🇿🇲", ZW: "🇿🇼",
};

const USD_TO_KRW = 1400;

function toKRW(usd: number): string {
  return `약 ${Math.round((usd * USD_TO_KRW) / 10000)}만원`;
}

interface TarotCardProps {
  state: "back" | "front" | "locked";
  cityData?: CityData | null;
  isSelected?: boolean;
  isFlipped?: boolean;
  onClick?: () => void;
}

/* ── Corner L-shaped flourish ── */
function CornerFlourish({
  position,
}: {
  position: "tl" | "tr" | "bl" | "br";
}) {
  const base = "absolute bg-border";
  const arm = 20;
  const t = 2;

  const posMap: Record<string, { h: string; v: string }> = {
    tl: {
      h: `top-0 left-0 rounded-tl-sm`,
      v: `top-0 left-0 rounded-tl-sm`,
    },
    tr: {
      h: `top-0 right-0 rounded-tr-sm`,
      v: `top-0 right-0 rounded-tr-sm`,
    },
    bl: {
      h: `bottom-0 left-0 rounded-bl-sm`,
      v: `bottom-0 left-0 rounded-bl-sm`,
    },
    br: {
      h: `bottom-0 right-0 rounded-br-sm`,
      v: `bottom-0 right-0 rounded-br-sm`,
    },
  };

  const p = posMap[position];

  return (
    <>
      <div className={`${base} ${p.h}`} style={{ width: arm, height: t }} />
      <div className={`${base} ${p.v}`} style={{ width: t, height: arm }} />
    </>
  );
}

/* ── Compass Rose (all CSS) ── */
function CompassRose() {
  return (
    <div className="relative flex items-center justify-center" style={{ width: 80, height: 80 }}>
      <div className="absolute rounded-full border border-border" style={{ width: 80, height: 80 }} />
      <div className="absolute bg-border" style={{ width: 80, height: 1, top: "50%", left: 0, transform: "translateY(-50%)" }} />
      <div className="absolute bg-border" style={{ width: 1, height: 80, left: "50%", top: 0, transform: "translateX(-50%)" }} />
      <div className="absolute bg-border" style={{ width: 80, height: 1, top: "50%", left: 0, transform: "translateY(-50%) rotate(45deg)" }} />
      <div className="absolute bg-border" style={{ width: 80, height: 1, top: "50%", left: 0, transform: "translateY(-50%) rotate(-45deg)" }} />
      <div className="absolute rounded-full border border-primary" style={{ width: 40, height: 40 }} />
      <div className="absolute rounded-full bg-primary" style={{ width: 8, height: 8 }} />
    </div>
  );
}

/* ── Back Face ── */
function BackFace({ isSelected }: { isSelected: boolean }) {
  return (
    <div
      className={`absolute inset-0 rounded-lg flex flex-col items-center justify-center gap-4 bg-card border-[1.5px] ${
        isSelected ? "border-primary" : "border-border"
      }`}
      style={{
        backfaceVisibility: "hidden",
        WebkitBackfaceVisibility: "hidden",
        ...(isSelected ? { boxShadow: "0 0 16px 4px var(--ring)" } : {}),
      }}
    >
      <div
        className={`absolute rounded border ${
          isSelected ? "border-primary" : "border-border"
        } pointer-events-none`}
        style={{ inset: 6 }}
      />
      <div className="absolute pointer-events-none" style={{ inset: 6 }}>
        <CornerFlourish position="tl" />
        <CornerFlourish position="tr" />
        <CornerFlourish position="bl" />
        <CornerFlourish position="br" />
      </div>
      <CompassRose />
      <span className="font-mono text-[10px] tracking-[0.35em] text-border">
        NNAI
      </span>
    </div>
  );
}

/* ── Front Face ── */
function FrontFace({ cityData }: { cityData: CityData }) {
  const flag = FLAG_EMOJI[cityData.country_id] ?? "🌍";
  const visaText =
    cityData.visa_free_days > 0
      ? `${cityData.visa_free_days}일`
      : "비자 필요";

  return (
    <div
      className="absolute inset-0 rounded-lg flex flex-col items-center justify-center px-4 py-5 bg-card border-[1.5px] border-border"
      style={{
        backfaceVisibility: "hidden",
        WebkitBackfaceVisibility: "hidden",
        transform: "rotateY(180deg)",
      }}
    >
      {/* Flag */}
      <span className="leading-none" style={{ fontSize: 32 }}>
        {flag}
      </span>

      {/* City name KR */}
      <p className="font-serif text-lg font-bold text-foreground text-center leading-tight mt-2">
        {cityData.city_kr}
      </p>

      {/* City name EN + country */}
      <p className="font-mono text-xs text-muted-foreground text-center leading-tight mt-0.5 tracking-wide">
        {cityData.city}, {cityData.country_id}
      </p>

      {/* Gold divider */}
      <div className="w-full h-px bg-border my-3" />

      {/* Metrics — horizontal compact */}
      <div className="w-full flex justify-around font-mono text-center">
        <div className="flex flex-col items-center gap-0.5">
          <span style={{ fontSize: 16 }}>💰</span>
          <span className="text-[13px] font-medium text-foreground">
            {toKRW(cityData.monthly_cost_usd)}
          </span>
        </div>
        <div className="flex flex-col items-center gap-0.5">
          <span style={{ fontSize: 16 }}>🛂</span>
          <span className="text-[13px] font-medium text-foreground">
            {visaText}
          </span>
        </div>
        {cityData.internet_mbps != null && (
          <div className="flex flex-col items-center gap-0.5">
            <span style={{ fontSize: 16 }}>📶</span>
            <span className="text-[13px] font-medium text-foreground">
              {cityData.internet_mbps}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Flip animation variants ── */
const cardVariants = {
  back: { rotateY: 0 },
  front: { rotateY: 180 },
};

/* ── Main Component ── */
export default function TarotCard({
  state,
  cityData,
  isSelected = false,
  isFlipped = false,
  onClick,
}: TarotCardProps) {
  const isLocked = state === "locked";

  return (
    <div
      className={`select-none aspect-[2/3] ${isLocked ? "" : "cursor-pointer"}`}
      style={{ perspective: 1000 }}
      onClick={isLocked ? undefined : onClick}
    >
      <motion.div
        className="relative w-full h-full"
        style={{ transformStyle: "preserve-3d" }}
        animate={isFlipped ? "front" : "back"}
        variants={cardVariants}
        transition={{ duration: 0.6, ease: "easeInOut" }}
      >
        {/* Back face — rotateY 0 (visible when not flipped) */}
        <BackFace isSelected={isSelected} />

        {/* Front face — rotateY 180 (visible when flipped) */}
        {cityData ? (
          <FrontFace cityData={cityData} />
        ) : (
          <div
            className="absolute inset-0 rounded-lg bg-card border-[1.5px] border-border"
            style={{
              backfaceVisibility: "hidden",
              WebkitBackfaceVisibility: "hidden",
              transform: "rotateY(180deg)",
            }}
          />
        )}
      </motion.div>

      {/* Lock overlay */}
      {isLocked && (
        <div className="absolute inset-0 rounded-lg flex items-center justify-center bg-card/60">
          <span style={{ fontSize: 32 }}>🔒</span>
        </div>
      )}
    </div>
  );
}
