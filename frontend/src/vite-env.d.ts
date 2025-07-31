/// <reference types="svelte" />
/// <reference types="vite/client" />

declare global {
  interface Window {
    navigate: (path: string) => void;
  }
}

export {};