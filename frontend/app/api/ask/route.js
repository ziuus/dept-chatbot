import { NextResponse } from "next/server";

function backendConfig() {
  return {
    baseUrl: process.env.BACKEND_BASE_URL || "http://127.0.0.1:8001",
    apiKey: process.env.BACKEND_API_KEY || ""
  };
}

export async function POST(request) {
  try {
    const body = await request.json();
    const question = (body?.question || "").trim();
    if (!question) {
      return NextResponse.json({ detail: "Question is required." }, { status: 400 });
    }

    const { baseUrl, apiKey } = backendConfig();
    const headers = { "Content-Type": "application/json" };
    if (apiKey) headers["X-API-Key"] = apiKey;

    const response = await fetch(`${baseUrl}/query`, {
      method: "POST",
      headers,
      body: JSON.stringify({ question }),
      cache: "no-store"
    });

    const payload = await response.json().catch(() => ({ detail: "Invalid backend response." }));
    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail || "Backend request failed." },
        { status: response.status }
      );
    }

    return NextResponse.json(payload, { status: 200 });
  } catch {
    return NextResponse.json({ detail: "Failed to process request." }, { status: 500 });
  }
}
