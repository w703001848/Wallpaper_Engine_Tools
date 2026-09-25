// Vitest runs from the project root so tests outside the renderer source tree are discoverable.
import { defineConfig } from 'vitest/config';

export default defineConfig({
  root: '.',
  test: {
    include: ['tests/**/*.test.ts'],
  },
});
