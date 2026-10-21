import path from 'node:path';
import react from '@vitejs/plugin-react';
import { writeSampleManifest } from '@zibby-run/app-kit/publish';
import { zibbyViteConfig } from '@zibby-run/app-kit/vite';
import autoprefixer from 'autoprefixer';
import tailwindcss from 'tailwindcss';
import { defineConfig } from 'vite';
import { buildZibbySample } from './static/src/lib/prompt.js';

/**
 * Swan on Zibby: the React app in static/ built as a static bundle into dist/, with
 * relative paths and every font in the bundle. The Python server is not part of it.
 */

/** Writes dist/zibby-sample.json, the requests Zibby replays to price the app. */
function zibbySampleManifest() {
  let outDir = 'dist';
  return {
    name: 'swan-zibby-sample',
    apply: 'build',
    configResolved(config) {
      outDir = path.resolve(config.root, config.build.outDir);
    },
    closeBundle() {
      writeSampleManifest(outDir, buildZibbySample());
    },
  };
}

export default defineConfig({
  root: 'static',
  base: zibbyViteConfig.base,
  publicDir: false,
  plugins: [react(), zibbySampleManifest()],
  css: {
    postcss: {
      plugins: [tailwindcss(path.resolve(import.meta.dirname, 'static/tailwind.config.cjs')), autoprefixer()],
    },
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    target: 'es2022',
    sourcemap: false,
    assetsInlineLimit: zibbyViteConfig.build.assetsInlineLimit,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    include: ['src/**/*.test.{js,jsx}'],
    css: false,
  },
});
