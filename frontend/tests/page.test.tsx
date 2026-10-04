import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import Home from "../app/page";

const successResponse = {
  status: "ok",
  mode: "DETERMINISTIC_STUB",
  artifacts: [
    {
      output_type: "executive_summary",
      content: "[DETERMINISTIC STUB]\nSource excerpt: Project Aurora.",
    },
  ],
  warnings: ["This is deterministic integration scaffolding; no AI was used."],
};

describe("walking skeleton workspace", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders a textarea, executive summary choice, and Generate Stub control", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Stringray", level: 1 })).toBeVisible();
    expect(screen.getByText("Phase 1 / walking skeleton · v0.2.0")).toBeVisible();
    expect(screen.getByRole("textbox", { name: /source text/i })).toBeVisible();
    expect(screen.getByRole("checkbox", { name: /executive summary/i })).toBeChecked();
    expect(screen.getByRole("button", { name: "Generate Stub" })).toBeVisible();
    expect(screen.getByText(/does not use AI or canonical analysis/)).toBeVisible();
  });

  test("renders a successful live API response and labels it as a stub", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify(successResponse), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    render(<Home />);
    fireEvent.change(screen.getByRole("textbox", { name: /source text/i }), {
      target: { value: "Project Aurora." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));

    expect(await screen.findByText("DETERMINISTIC STUB / NO AI")).toBeVisible();
    expect(screen.getByText(/^\[DETERMINISTIC STUB\]/)).toBeVisible();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  test("shows a friendly backend error without fallback content", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ detail: "unsupported output" }), { status: 422 }),
    );
    render(<Home />);
    fireEvent.change(screen.getByRole("textbox", { name: /source text/i }), {
      target: { value: "Input" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("unsupported output");
    expect(screen.queryByText(/^\[DETERMINISTIC STUB\]/)).not.toBeInTheDocument();
  });

  test("shows an explicit connection error when fetch fails", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("Failed to fetch"));
    render(<Home />);
    fireEvent.change(screen.getByRole("textbox", { name: /source text/i }), {
      target: { value: "Input" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/could not connect/i);
    expect(screen.queryByText(/^\[DETERMINISTIC STUB\]/)).not.toBeInTheDocument();
  });

  test("empty submission is rejected before a successful result", async () => {
    render(<Home />);
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/enter source text/i);
    expect(fetch).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByText("DETERMINISTIC STUB / NO AI")).not.toBeInTheDocument());
  });

  test("shows loading and disables submission while the request is pending", async () => {
    let resolveRequest!: (response: Response) => void;
    vi.mocked(fetch).mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    render(<Home />);
    fireEvent.change(screen.getByRole("textbox", { name: /source text/i }), {
      target: { value: "Input" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));
    expect(screen.getByRole("button", { name: "Generating stub…" })).toBeDisabled();
    await act(async () => resolveRequest(new Response(JSON.stringify(successResponse))));
    expect(screen.getByRole("button", { name: "Generate Stub" })).toBeEnabled();
  });

  test("rejects malformed success responses rather than rendering arbitrary data", async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({
      ...successResponse,
      warnings: [{ arbitrary: "not a string" }],
    })));
    render(<Home />);
    fireEvent.change(screen.getByRole("textbox", { name: /source text/i }), {
      target: { value: "Input" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Stub" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/unexpected transform response/i);
    expect(screen.queryByText(/^\[DETERMINISTIC STUB\]/)).not.toBeInTheDocument();
  });
});
