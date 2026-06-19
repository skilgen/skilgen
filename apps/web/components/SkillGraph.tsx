"use client";

import { useCallback, useEffect, useRef } from "react";

type SourceNode = {
  id: string;
  label: string;
  colorToken: string;
  colorFallback: string;
  x: number;
  y: number;
};

type RuntimeNode = SourceNode & {
  active: boolean;
  activeTimer: number;
  baseRadius: number;
  color: string;
  driftPhase: number;
  driftSpeed: number;
  pulsePhase: number;
  pulseSpeed: number;
  px: number;
  py: number;
};

type RuntimeEdge = {
  source: string;
  target: string;
  particleProgress: number;
  particleSpeed: number;
  pauseUntil: number;
};

const sourceNodes: SourceNode[] = [
  { id: "auth", label: "auth", colorToken: "--node-auth", colorFallback: "#C9973A", x: 0.18, y: 0.22 },
  { id: "billing", label: "billing", colorToken: "--node-billing", colorFallback: "#3DD68C", x: 0.72, y: 0.18 },
  { id: "api", label: "api", colorToken: "--node-api", colorFallback: "#A78BFA", x: 0.45, y: 0.35 },
  { id: "payments", label: "payments", colorToken: "--node-billing", colorFallback: "#3DD68C", x: 0.82, y: 0.42 },
  { id: "security", label: "security", colorToken: "--node-security", colorFallback: "#F25F5C", x: 0.12, y: 0.55 },
  { id: "data", label: "data", colorToken: "--node-data", colorFallback: "#F5A623", x: 0.58, y: 0.62 },
  { id: "core", label: "core", colorToken: "--node-core", colorFallback: "#8888AA", x: 0.35, y: 0.58 },
  { id: "infra", label: "infra", colorToken: "--node-infra", colorFallback: "#22D3EE", x: 0.68, y: 0.75 },
  { id: "tests", label: "tests", colorToken: "--node-tests", colorFallback: "#3DD68C", x: 0.25, y: 0.78 },
  { id: "models", label: "models", colorToken: "--node-api", colorFallback: "#A78BFA", x: 0.88, y: 0.28 },
  { id: "webhooks", label: "webhooks", colorToken: "--node-auth", colorFallback: "#C9973A", x: 0.52, y: 0.15 },
  { id: "delivery", label: "delivery", colorToken: "--node-data", colorFallback: "#F5A623", x: 0.08, y: 0.38 },
  { id: "agents", label: "agents", colorToken: "--node-infra", colorFallback: "#22D3EE", x: 0.78, y: 0.58 },
  { id: "score", label: "score", colorToken: "--node-tests", colorFallback: "#3DD68C", x: 0.42, y: 0.82 },
  { id: "workspace", label: "workspace", colorToken: "--node-auth", colorFallback: "#C9973A", x: 0.15, y: 0.88 },
  { id: "generators", label: "generators", colorToken: "--node-api", colorFallback: "#A78BFA", x: 0.62, y: 0.88 },
  { id: "registry", label: "registry", colorToken: "--node-security", colorFallback: "#F25F5C", x: 0.88, y: 0.72 },
  { id: "cli", label: "cli", colorToken: "--node-infra", colorFallback: "#22D3EE", x: 0.32, y: 0.12 },
];

const sourceEdges = [
  ["auth", "security"],
  ["auth", "api"],
  ["auth", "core"],
  ["billing", "payments"],
  ["billing", "api"],
  ["billing", "data"],
  ["api", "core"],
  ["api", "agents"],
  ["api", "webhooks"],
  ["core", "models"],
  ["core", "score"],
  ["core", "delivery"],
  ["data", "models"],
  ["data", "infra"],
  ["security", "delivery"],
  ["security", "core"],
  ["agents", "score"],
  ["agents", "registry"],
  ["workspace", "cli"],
  ["workspace", "generators"],
  ["generators", "registry"],
  ["score", "delivery"],
  ["infra", "registry"],
  ["tests", "core"],
  ["tests", "score"],
  ["webhooks", "delivery"],
  ["models", "billing"],
] as const;

const alwaysLabel = new Set(["auth", "api", "core", "data", "agents", "security"]);

function randomBetween(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function hexToRgb(hex: string) {
  const normalized = hex.replace("#", "");
  const value = Number.parseInt(normalized, 16);

  return {
    r: (value >> 16) & 255,
    g: (value >> 8) & 255,
    b: value & 255,
  };
}

function rgba(hex: string, alpha: number) {
  const { r, g, b } = hexToRgb(hex);

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function blendHex(a: string, b: string) {
  const first = hexToRgb(a);
  const second = hexToRgb(b);

  return `rgb(${Math.round((first.r + second.r) / 2)}, ${Math.round((first.g + second.g) / 2)}, ${Math.round(
    (first.b + second.b) / 2,
  )})`;
}

function cssVar(name: string, fallback: string) {
  if (typeof window === "undefined") {
    return fallback;
  }

  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

export default function SkillGraph() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameRef = useRef<number | null>(null);
  const nodesRef = useRef<RuntimeNode[]>([]);
  const edgesRef = useRef<RuntimeEdge[]>([]);
  const sizeRef = useRef({ dpr: 1, height: 0, width: 0 });

  const initialiseGraph = useCallback(() => {
    nodesRef.current = sourceNodes.map((node) => ({
      ...node,
      active: Math.random() > 0.58,
      activeTimer: randomBetween(2, 4),
      baseRadius: ["auth", "api", "core"].includes(node.id) ? 6 : 4,
      color: cssVar(node.colorToken, node.colorFallback),
      driftPhase: randomBetween(0, Math.PI * 2),
      driftSpeed: randomBetween(0.0003, 0.0008),
      pulsePhase: randomBetween(0, Math.PI * 2),
      pulseSpeed: randomBetween(0.01, 0.02),
      px: 0,
      py: 0,
    }));

    edgesRef.current = sourceEdges.map(([source, target]) => ({
      source,
      target,
      particleProgress: Math.random(),
      particleSpeed: randomBetween(0.002, 0.004),
      pauseUntil: 0,
    }));
  }, []);

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }

    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = Math.max(1, Math.floor(rect.width * dpr));
    canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    sizeRef.current = { dpr, height: rect.height, width: rect.width };
  }, []);

  const drawParticle = useCallback(
    (
      context: CanvasRenderingContext2D,
      from: RuntimeNode,
      to: RuntimeNode,
      progress: number,
      radius: number,
    ) => {
      const x = from.px + (to.px - from.px) * progress;
      const y = from.py + (to.py - from.py) * progress;
      const color = blendHex(from.color, to.color);

      context.beginPath();
      context.fillStyle = color.replace("rgb", "rgba").replace(")", ", 0.2)");
      context.arc(x, y, 4, 0, Math.PI * 2);
      context.fill();

      context.beginPath();
      context.fillStyle = color.replace("rgb", "rgba").replace(")", ", 0.8)");
      context.arc(x, y, radius, 0, Math.PI * 2);
      context.fill();
    },
    [],
  );

  const draw = useCallback(
    (timestamp: number) => {
      const canvas = canvasRef.current;
      const context = canvas?.getContext("2d");

      if (!canvas || !context) {
        return;
      }

      const { dpr, height, width } = sizeRef.current;
      const t = timestamp / 1000;
      const nodes = nodesRef.current;
      const edges = edgesRef.current;

      context.clearRect(0, 0, canvas.width, canvas.height);
      context.save();
      context.scale(dpr, dpr);

      for (const node of nodes) {
        node.activeTimer -= 1 / 60;

        if (node.activeTimer <= 0) {
          node.active = !node.active;
          node.activeTimer = randomBetween(2, 4);
        }

        node.px = (node.x + Math.sin(t * node.driftSpeed + node.driftPhase) * 0.02) * width;
        node.py = (node.y + Math.cos(t * node.driftSpeed * 0.7 + node.driftPhase) * 0.02) * height;
      }

      const nodeById = new Map(nodes.map((node) => [node.id, node]));

      for (const edge of edges) {
        const from = nodeById.get(edge.source);
        const to = nodeById.get(edge.target);

        if (!from || !to) {
          continue;
        }

        const active = from.active || to.active;
        const gradient = context.createLinearGradient(from.px, from.py, to.px, to.py);
        gradient.addColorStop(0, rgba(from.color, active ? 0.2 : 0.06));
        gradient.addColorStop(1, rgba(to.color, active ? 0.2 : 0.06));

        context.beginPath();
        context.strokeStyle = gradient;
        context.lineWidth = active ? 1 : 0.5;
        context.moveTo(from.px, from.py);
        context.lineTo(to.px, to.py);
        context.stroke();

        if (edge.pauseUntil <= t) {
          edge.particleProgress += edge.particleSpeed;
        }

        if (edge.particleProgress >= 1) {
          edge.particleProgress = 0;
          edge.pauseUntil = t + randomBetween(1, 3);
        }

        if (edge.pauseUntil <= t) {
          drawParticle(context, from, to, edge.particleProgress, 1.5);

          if (active) {
            drawParticle(context, from, to, (edge.particleProgress * 1.7) % 1, 1.25);
          }
        }
      }

      context.textAlign = "center";
      context.textBaseline = "bottom";
      context.font = `11px ${getComputedStyle(document.body).fontFamily}`;

      for (const node of nodes) {
        const radius = node.baseRadius + Math.sin(t * node.pulseSpeed + node.pulsePhase) * 2 + (node.active ? 2 : 0);

        context.beginPath();
        context.strokeStyle = rgba(node.color, 0.08);
        context.lineWidth = 1;
        context.arc(node.px, node.py, radius * 3.5, 0, Math.PI * 2);
        context.stroke();

        context.beginPath();
        context.strokeStyle = rgba(node.color, 0.15);
        context.lineWidth = 0.5;
        context.arc(node.px, node.py, radius * 2, 0, Math.PI * 2);
        context.stroke();

        context.beginPath();
        context.fillStyle = rgba(node.color, node.active ? 1 : 0.85);
        context.arc(node.px, node.py, Math.max(2, radius), 0, Math.PI * 2);
        context.fill();

        if (node.active || alwaysLabel.has(node.id)) {
          context.fillStyle = rgba(node.color, node.active ? 0.9 : 0.6);
          context.fillText(node.label, node.px, node.py - radius * 3.7);
        }
      }

      context.restore();
      frameRef.current = requestAnimationFrame(draw);
    },
    [drawParticle],
  );

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return undefined;
    }

    initialiseGraph();
    resizeCanvas();

    const observer = new ResizeObserver(resizeCanvas);
    observer.observe(canvas);
    frameRef.current = requestAnimationFrame(draw);

    return () => {
      observer.disconnect();

      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [draw, initialiseGraph, resizeCanvas]);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none absolute inset-0 z-0 h-full w-full" />;
}
