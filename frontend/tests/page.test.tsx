import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Home from "../app/page";

test("identifies Stringray and its foundation-only status", () => {
  render(<Home />);

  expect(screen.getByRole("heading", { name: "Stringray", level: 1 })).toBeVisible();
  expect(screen.getByText("Phase 0 / foundation · v0.1.0")).toBeVisible();
  expect(screen.getByText("AI transformation is not implemented in v0.1.0.")).toBeVisible();
});
