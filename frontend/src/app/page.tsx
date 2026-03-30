import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#0a0c10] font-mono">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold text-white tracking-tight">
          NomadNavigator <span className="text-amber-400">AI</span>
        </h1>
        <p className="text-[#6b7280] text-sm">디지털 노마드 이민 설계 서비스</p>
        <Link
          href="/dev"
          className="inline-flex items-center gap-2 px-6 py-3 bg-amber-400 text-black font-bold text-sm rounded-xl hover:bg-amber-300 transition-colors"
        >
          <span className="w-2 h-2 rounded-full bg-black/40 animate-pulse" />
          Backend Test
        </Link>
      </div>
    </div>
  );
}
