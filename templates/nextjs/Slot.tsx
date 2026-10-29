// A gap only the business can fill: a price, a review count, a licence, a photo.
// It renders on purpose, in amber, so a page can never ship an invented number.
// Write slots inside copy as [[YOUR PRICE RANGE]] and pass the string to fill().
// Copy to components/Slot.tsx in the user's site. Every token has a fallback, so it works anywhere.
import React from "react";

const SLOT_STYLE: React.CSSProperties = {
  display: "inline-block", padding: "0 8px", margin: "0 2px", borderRadius: "6px",
  border: "1.5px dashed var(--status-warning, #B7791F)", background: "var(--status-warning-soft, #FBF5E9)",
  color: "var(--status-warning, #B7791F)", fontWeight: 600, fontSize: "0.92em", lineHeight: 1.6,
};

export function Slot({ children }: { children: React.ReactNode }) {
  return <span data-slot="fill-in" style={SLOT_STYLE}>{children}</span>;
}

/** Turns "Most clears cost [[YOUR PRICE RANGE]]." into text with a visible slot. */
export function fill(text: string): React.ReactNode {
  return text.split(/\[\[(.+?)\]\]/).map((part, i) => (i % 2 ? <Slot key={i}>{part}</Slot> : part));
}

/** True when copy still holds a slot - kept out of schema until it is filled. */
export function hasSlot(text: string) {
  return /\[\[.+?\]\]/.test(text);
}

/** A photo the business has to take. Never stock, never AI: a real job. */
export function PhotoSlot({ label, onBrand = false }: { label: string; onBrand?: boolean }) {
  return (
    <div data-slot="photo" style={{
      aspectRatio: "4 / 3", width: "100%", borderRadius: "var(--radius-media, 16px)", display: "grid", placeItems: "center",
      padding: "var(--space-6, 24px)", textAlign: "center",
      border: `2px dashed ${onBrand ? "rgba(255, 255, 255, 0.55)" : "var(--status-warning, #B7791F)"}`,
      background: onBrand ? "rgba(255, 255, 255, 0.08)" : "var(--status-warning-soft, #FBF5E9)",
      color: onBrand ? "var(--white, #fff)" : "var(--status-warning, #B7791F)",
    }}>
      <span style={{ display: "grid", gap: "6px" }}>
        <strong style={{ font: "var(--type-label, 600 11px/1.2 system-ui, sans-serif)", letterSpacing: "var(--track-label, 0.08em)", textTransform: "uppercase" }}>Your photo here</strong>
        <span style={{ font: "var(--type-body-sm, 14px/1.5 system-ui, sans-serif)" }}>{label}</span>
      </span>
    </div>
  );
}
