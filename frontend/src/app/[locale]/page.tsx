"use client";

import Link from "next/link";
import { motion } from "framer-motion";

const fadeUp = (delay: number) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const, delay } },
});

export default function Home() {
  return (
    <div className="mx-auto flex min-h-screen max-w-sm w-full flex-col items-center justify-center px-4">
      {/* 지구본 */}
      <motion.div {...fadeUp(0.2)} className="mb-6">
        <img src="/earth_web.gif" alt="" width={96} height={96} className="mx-auto" />
      </motion.div>

      {/* 헤드라인 */}
      <motion.div {...fadeUp(0.4)} className="text-center mb-8">
        <h1 className="text-2xl font-bold text-foreground leading-snug mb-3">
          나는 어떤 노마드일까?
        </h1>
        <p className="text-sm text-muted-foreground">
          5분 유형 테스트로 내 유형을 찾고,<br />나에게 맞는 도시를 만나보세요.
        </p>
      </motion.div>

      {/* CTA */}
      <div className="w-full space-y-4">
        <motion.div {...fadeUp(0.6)}>
          <Link
            href="/onboarding/quiz"
            className="block w-full bg-primary py-3.5 text-center text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            내 유형 찾아보기
          </Link>
        </motion.div>

        <motion.div {...fadeUp(0.8)}>
          <Link
            href="/onboarding/form"
            className="block w-full border border-border py-3.5 text-center text-sm font-medium text-foreground transition-colors hover:bg-accent"
          >
            도시 추천 바로 받기
          </Link>
          <p className="text-xs text-muted-foreground text-center mt-2 opacity-50">
            유형 테스트를 먼저 하면 추천이 더 정확해져요
          </p>
        </motion.div>
      </div>
    </div>
  );
}
