"use client";

import { type FormEvent, useState } from "react";

import { requestTransform, type TransformResponse } from "../lib/api";

export default function Home() {
  const [sourceText, setSourceText] = useState("");
  const [result, setResult] = useState<TransformResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!sourceText.trim()) {
      setError("Enter source text before generating the stub.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await requestTransform({
        source: { type: "text", text: sourceText },
        outputs: ["executive_summary"],
        controls: {
          target_audience: null,
          tone: null,
          language: null,
          detail_level: null,
          communication_objective: null,
          content_style: null,
        },
      });
      setResult(response);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The transform request failed. Try again.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <p className="mb-4 inline-block rounded border border-slate-300 px-3 py-1 text-sm">
        Phase 1 / walking skeleton · v0.2.0
      </p>
      <h1 className="text-4xl font-semibold tracking-tight">Stringray</h1>
      <p className="mt-4 text-lg">One plain-text request through the live API.</p>
      <p className="mt-2 text-sm text-slate-600">
        This workspace proves integration only. It does not use AI or canonical analysis.
      </p>

      <form className="mt-10 space-y-6" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm font-medium" htmlFor="source-text">
            Source text
          </label>
          <textarea
            className="mt-2 min-h-48 w-full rounded border border-slate-300 bg-white p-3 text-sm shadow-sm outline-none focus:border-slate-500"
            id="source-text"
            onChange={(event) => setSourceText(event.target.value)}
            placeholder="Paste plain text for the deterministic integration stub."
            value={sourceText}
          />
        </div>

        <fieldset>
          <legend className="text-sm font-medium">Output</legend>
          <label className="mt-2 flex items-center gap-2 text-sm">
            <input checked disabled readOnly type="checkbox" />
            Executive Summary
          </label>
          <p className="mt-1 text-xs text-slate-500">
            The only output path exposed in Phase 1.
          </p>
        </fieldset>

        <button
          className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-wait disabled:opacity-60"
          disabled={isLoading}
          type="submit"
        >
          {isLoading ? "Generating stub…" : "Generate Stub"}
        </button>
      </form>

      {error && (
        <p className="mt-6 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-900" role="alert">
          {error}
        </p>
      )}

      {result && (
        <section aria-live="polite" className="mt-10 rounded border border-amber-300 bg-amber-50 p-5">
          <p className="text-xs font-semibold tracking-wide text-amber-900">DETERMINISTIC STUB / NO AI</p>
          <h2 className="mt-2 text-xl font-semibold">Executive Summary</h2>
          <pre className="mt-4 whitespace-pre-wrap font-sans text-sm text-slate-800">
            {result.artifacts[0].content}
          </pre>
          <ul className="mt-4 list-disc pl-5 text-xs text-amber-900">
            {result.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </section>
      )}
    </main>
  );
}
