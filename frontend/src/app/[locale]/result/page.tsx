import { useTranslations } from "next-intl";

export default function ResultPage() {
  const t = useTranslations("result");
  return (
    <div className="flex min-h-dvh items-center justify-center px-5">
      <p className="font-serif text-sm text-[var(--onboarding-text-secondary)]">
        {t("placeholder")}
      </p>
    </div>
  );
}
