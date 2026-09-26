/** Verifies persisted library view preferences remain compatible with old or manually edited settings. */
import { describe, expect, it } from "vitest";
import { normalizeLibraryView } from "../electron/settings.js";

describe("library view settings", () => {
  it("keeps supported filters and ordering", () => {
    expect(
      normalizeLibraryView({
        sources: ["backup", "nas"],
        types: ["video", "scene"],
        sort: "title",
        descending: false,
      }),
    ).toEqual({
      sources: ["backup", "nas"],
      types: ["video", "scene"],
      sort: "title",
      descending: false,
    });
  });

  it("filters invalid values and supplies defaults for older settings", () => {
    const edited = normalizeLibraryView({
      sources: ["backup", "invalid" as "backup"],
      types: ["video", "invalid" as "video"],
      sort: "invalid" as "title",
    });
    expect(edited).toEqual({
      sources: ["backup"],
      types: ["video"],
      sort: "updatedAt",
      descending: true,
    });
  });
});
