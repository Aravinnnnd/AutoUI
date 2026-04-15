import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Use a non-privileged port for local dev to avoid permission errors.
  server: { port: 5174 },
});
