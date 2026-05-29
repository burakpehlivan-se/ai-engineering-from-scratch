// Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/code/verify.ts
// Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import { execFileSync } from "node:child_process";
import process from "node:process";

type ProbeFn = () => { ok: boolean; detail?: string };

type Probe = {
  name: string;
  required: boolean;
  run: ProbeFn;
};

function whichVersion(cmd: string, args: string[] = ["--version"]): ReturnType<ProbeFn> {
  try {
    const out = execFileSync(cmd, args, {
      stdio: ["ignore", "pipe", "ignore"],
      encoding: "utf8",
      timeout: 4000,
    });
    return { ok: true, detail: out.trim().split("\n")[0] };
  } catch {
    return { ok: false };
  }
}

const PROBES: Probe[] = [
  {
    name: "Node.js 20+",
    required: true,
    run: () => {
      const major = Number.parseInt(process.versions.node.split(".")[0]!, 10);
      return { ok: major >= 20, detail: `v${process.versions.node}` };
    },
  },
  {
    name: "TypeScript çalıştırıcı (tsx)",
    required: false,
    run: () => whichVersion("npx", ["-y", "tsx", "--version"]),
  },
  {
    name: "Git",
    required: true,
    run: () => whichVersion("git"),
  },
  {
    name: "Python 3.10+",
    required: true,
    run: () => {
      const probe = whichVersion("python3");
      if (!probe.ok || !probe.detail) return probe;
      const match = probe.detail.match(/(\d+)\.(\d+)/);
      if (!match) return { ok: false, detail: probe.detail };
      const [major, minor] = [Number(match[1]), Number(match[2])];
      const ok = major > 3 || (major === 3 && minor >= 10);
      return { ok, detail: probe.detail };
    },
  },
  {
    name: "Rust (cargo)",
    required: false,
    run: () => whichVersion("cargo"),
  },
  {
    name: "Deno",
    required: false,
    run: () => whichVersion("deno"),
  },
];

function run(): number {
  process.stdout.write("\n=== Sıfırdan Yapay Zeka Mühendisliği — Ortam Kontrolü ===\n\n");

  let requiredPassed = 0;
  let requiredTotal = 0;

  for (const probe of PROBES) {
    const result = probe.run();
    const tag = result.ok ? "GEÇTİ" : "KALDI";
    const detail = result.detail ? ` (${result.detail})` : "";
    const flag = probe.required ? "" : "  [isteğe bağlı]";
    process.stdout.write(`  [${tag}] ${probe.name}${detail}${flag}\n`);
    if (probe.required) {
      requiredTotal += 1;
      if (result.ok) requiredPassed += 1;
    }
  }

  process.stdout.write(`\nSonuç: ${requiredPassed}/${requiredTotal} zorunlu kontrol geçildi\n`);
  if (requiredPassed === requiredTotal) {
    process.stdout.write("\nHazırsınız. Faz 1 ile başlayın.\n\n");
    return 0;
  }
  process.stdout.write("\nYukarıdaki başarısız zorunlu kontrolleri düzeltin, sonra tekrar çalıştırın.\n\n");
  return 1;
}

process.exit(run());
