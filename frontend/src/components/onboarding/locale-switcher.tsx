"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";

export function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  function switchLocale() {
    const newLocale = locale === "ko" ? "en" : "ko";
    router.replace(pathname, { locale: newLocale });
  }

  return (
    <button
      type="button"
      onClick={switchLocale}
      className="fixed right-4 top-4 z-50 rounded-lg border border-[var(--onboarding-card-border)] bg-[var(--onboarding-card-bg)] px-3 py-1.5 font-serif text-xs text-[var(--onboarding-text-secondary)] transition-colors hover:border-[var(--onboarding-card-border-active)] hover:text-[var(--onboarding-text-primary)]"
    >
      {locale === "ko" ? "EN" : "KO"}
    </button>
  );
}
