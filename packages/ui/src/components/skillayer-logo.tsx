import type { SVGProps } from "react";

import { cn } from "../lib/utils";

type SkillayerLogoProps = SVGProps<SVGSVGElement> & {
  showWordmark?: boolean;
};

const hexagons = [
  { points: "64 0 128 32 128 80 64 112 0 80 0 32", tone: "gold" },
  { points: "208 0 272 32 272 80 208 112 144 80 144 32", tone: "white" },
  { points: "352 0 416 32 416 80 352 112 288 80 288 32", tone: "white" },
  { points: "496 0 560 32 560 80 496 112 432 80 432 32", tone: "gold" },
  { points: "136 96 200 128 200 176 136 208 72 176 72 128", tone: "white" },
  { points: "280 96 344 128 344 176 280 208 216 176 216 128", tone: "white" },
  { points: "424 96 488 128 488 176 424 208 360 176 360 128", tone: "white" },
] as const;

export function SkillayerLogo({ className, showWordmark = true, ...props }: SkillayerLogoProps) {
  return (
    <svg
      aria-label="Skillayer"
      className={cn("h-7 w-auto overflow-visible", className)}
      fill="none"
      role="img"
      viewBox={showWordmark ? "0 0 920 208" : "0 0 560 208"}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <g strokeLinecap="round" strokeLinejoin="round" strokeWidth="10">
        {hexagons.map((hexagon) => (
          <polygon
            key={hexagon.points}
            points={hexagon.points}
            stroke={hexagon.tone === "gold" ? "var(--logo-gold, #F7DF7C)" : "var(--logo-white, #F7F8FF)"}
          />
        ))}
      </g>

      {showWordmark ? (
        <text
          fill="var(--text-primary, #F0F0FF)"
          fontFamily="var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif"
          fontSize="76"
          fontWeight="700"
          letterSpacing="-2"
          x="612"
          y="126"
        >
          Skillayer
        </text>
      ) : null}
    </svg>
  );
}
