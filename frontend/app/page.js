"use client";

import { useEffect, useRef, useState } from "react";

function createSpeechRecognition() {
  if (typeof window === "undefined") return null;
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;
  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  return recognition;
}

function normalizeMessage(error) {
  if (!error) return "Something went wrong.";
  if (typeof error === "string") return error;
  return error.message || "Something went wrong.";
}

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [route, setRoute] = useState("");
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    setMounted(true);
    setSpeechSupported(
      typeof window !== "undefined" &&
        Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
    );
  }, []);

  const speak = (text) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const askQuestion = async (text) => {
    const cleaned = (text || "").trim();
    if (!cleaned) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleaned })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "Request failed.");
      }
      setAnswer(data.answer || "");
      setRoute(data.route || "");
      if (data.answer) speak(data.answer);
    } catch (err) {
      setError(normalizeMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const onStartListening = () => {
    setError("");
    const recognition = createSpeechRecognition();
    if (!recognition) {
      setError("Speech recognition is not supported in this browser.");
      return;
    }
    recognitionRef.current = recognition;
    recognition.onstart = () => setListening(true);
    recognition.onerror = (event) => {
      setListening(false);
      setError(`Voice error: ${event.error || "unknown"}`);
    };
    recognition.onend = () => setListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      setQuestion(transcript);
      askQuestion(transcript);
    };
    recognition.start();
  };

  const onStopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  return (
    <main className="page">
      <section className="card">
        <h1>Department Voice Assistant</h1>
        <p className="subtitle">
          Ask about faculty, subjects, cabins, semesters, and availability.
        </p>

        <div className="controls">
          {!listening ? (
            <button className="btn primary" onClick={onStartListening} disabled={loading}>
              {!mounted
                ? "Checking Voice Support..."
                : speechSupported
                  ? "Start Voice Question"
                  : "Voice Not Supported"}
            </button>
          ) : (
            <button className="btn danger" onClick={onStopListening}>
              Stop Listening
            </button>
          )}
          <button
            className="btn ghost"
            onClick={() => askQuestion(question)}
            disabled={loading || !question.trim()}
          >
            Ask Typed Question
          </button>
        </div>

        <label className="label" htmlFor="question">
          Your Question
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Who teaches Cloud Computing?"
          rows={3}
        />

        {loading && <p className="status">Getting answer...</p>}
        {error && <p className="status error">{error}</p>}
        {answer && (
          <div className="answerBox">
            <p className="route">Route: {route || "unknown"}</p>
            <p>{answer}</p>
            <button className="btn ghost" onClick={() => speak(answer)}>
              Replay Audio
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
