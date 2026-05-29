// Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/04-apis-and-keys/code/first_api_call.ts
// Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import process from "node:process";

type MessagesRequest = {
  model: string;
  max_tokens: number;
  messages: { role: "user" | "assistant"; content: string }[];
};

type MessagesResponse = {
  content: { type: string; text: string }[];
  usage: { input_tokens: number; output_tokens: number };
};

function loadDotenv(path: string): Record<string, string> {
  let raw: string;
  try {
    raw = readFileSync(path, "utf8");
  } catch {
    return {};
  }
  const out: Record<string, string> = {};
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }
  return out;
}

function mergeEnv(): NodeJS.ProcessEnv {
  const fromFile = loadDotenv(resolve(process.cwd(), ".env"));
  return { ...fromFile, ...process.env };
}

const MOCK_RESPONSE: MessagesResponse = {
  content: [
    {
      type: "text",
      text: "Sinir ağı, bir kayıp sinyaline karşı ağırlıkları ayarlayarak örüntüleri öğrenen farklılaştırılabilir fonksiyonların bir yığınıdır.",
    },
  ],
  usage: { input_tokens: 12, output_tokens: 28 },
};

async function callMessages(apiKey: string, request: MessagesRequest): Promise<MessagesResponse> {
  if (process.env.MOCK === "1" || apiKey === "mock") {
    return MOCK_RESPONSE;
  }

  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(request),
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`anthropic ${resp.status}: ${body.slice(0, 200)}`);
  }
  return (await resp.json()) as MessagesResponse;
}

async function main(): Promise<number> {
  const env = mergeEnv();
  const apiKey = env.ANTHROPIC_API_KEY ?? "mock";
  const usingMock = process.env.MOCK === "1" || apiKey === "mock";

  process.stdout.write("=== API Çağrıları ===\n\n");
  process.stdout.write(
    usingMock
      ? "Mod: SAHTE (ağ yok). Canlı bir çağrı için MOCK'u kaldırın ve ANTHROPIC_API_KEY ayarlayın.\n\n"
      : "Mod: CANLI.\n\n",
  );

  const request: MessagesRequest = {
    model: "claude-sonnet-4-6",
    max_tokens: 256,
    messages: [{ role: "user", content: "Sinir ağı tek cümlede nedir?" }],
  };

  try {
    const response = await callMessages(apiKey, request);
    const text = response.content[0]?.text ?? "";
    process.stdout.write(`yanıt: ${text}\n`);
    process.stdout.write(
      `token'lar: ${response.usage.input_tokens} giriş, ${response.usage.output_tokens} çıkış\n`,
    );
    return 0;
  } catch (err) {
    process.stderr.write(`istek başarısız: ${(err as Error).message}\n`);
    return 1;
  }
}

main().then((code) => process.exit(code));
