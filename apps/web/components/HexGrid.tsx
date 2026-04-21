"use client";

import { useCallback, useEffect, useRef } from "react";

type CellState = "incoming" | "locking" | "locked" | "active" | "departing";

type Slot = {
  id: number;
  label: string;
  targetX: number;
  targetY: number;
};

type Cell = Slot & {
  activeUntil: number;
  activationAt: number;
  departAt: number;
  departureX: number;
  departureY: number;
  lockStartedAt: number;
  opacity: number;
  phase: number;
  speed: number;
  state: CellState;
  x: number;
  y: number;
};

type FloatingHex = {
  opacity: number;
  phase: number;
  size: number;
  vx: number;
  vy: number;
  x: number;
  y: number;
};

type EdgeParticle = {
  direction: 1 | -1;
  progress: number;
};

const HEX_SIZE = 32;
const GRID_SIZE = 28;
const FLOATING_COUNT = 20;
const HORIZONTAL_SPACING = HEX_SIZE * 1.5;
const VERTICAL_SPACING = HEX_SIZE * Math.sqrt(3);
const LABELS = ["auth", "security", "delivery", "workspace", "billing", "api", "agents"];
const ADJACENCY = [
  [0, 1],
  [0, 2],
  [1, 3],
  [2, 3],
  [4, 5],
  [4, 6],
  [5, 6],
] as const;

function randomBetween(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function drawFlatHex(context: CanvasRenderingContext2D, cx: number, cy: number, size: number) {
  context.beginPath();

  for (let index = 0; index < 6; index += 1) {
    const angle = (Math.PI / 180) * 60 * index;
    const x = cx + size * Math.cos(angle);
    const y = cy + size * Math.sin(angle);

    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  }

  context.closePath();
}

function cssVar(name: string, fallback: string) {
  if (typeof window === "undefined") {
    return fallback;
  }

  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

function spawnFromEdge(width: number, height: number) {
  const edge = Math.floor(Math.random() * 4);

  if (edge === 0) {
    return { x: randomBetween(0, width), y: -HEX_SIZE * 2 };
  }

  if (edge === 1) {
    return { x: width + HEX_SIZE * 2, y: randomBetween(0, height) };
  }

  if (edge === 2) {
    return { x: randomBetween(0, width), y: height + HEX_SIZE * 2 };
  }

  return { x: -HEX_SIZE * 2, y: randomBetween(0, height) };
}

function targetEdge(width: number, height: number) {
  const edge = Math.floor(Math.random() * 4);

  if (edge === 0) {
    return { x: randomBetween(0, width), y: -HEX_SIZE * 3 };
  }

  if (edge === 1) {
    return { x: width + HEX_SIZE * 3, y: randomBetween(0, height) };
  }

  if (edge === 2) {
    return { x: randomBetween(0, width), y: height + HEX_SIZE * 3 };
  }

  return { x: -HEX_SIZE * 3, y: randomBetween(0, height) };
}

function buildSlots(width: number, height: number): Slot[] {
  const leftCenter = { x: width * 0.18, y: height * 0.5 };
  const rightCenter = { x: width * 0.82, y: height * 0.45 };
  const rawSlots = [
    { id: 0, label: LABELS[0], targetX: leftCenter.x - HORIZONTAL_SPACING / 2, targetY: leftCenter.y - VERTICAL_SPACING / 2 },
    { id: 1, label: LABELS[1], targetX: leftCenter.x + HORIZONTAL_SPACING / 2, targetY: leftCenter.y - VERTICAL_SPACING / 2 },
    { id: 2, label: LABELS[2], targetX: leftCenter.x - HORIZONTAL_SPACING / 2, targetY: leftCenter.y + VERTICAL_SPACING / 2 },
    { id: 3, label: LABELS[3], targetX: leftCenter.x + HORIZONTAL_SPACING / 2, targetY: leftCenter.y + VERTICAL_SPACING / 2 },
    { id: 4, label: LABELS[4], targetX: rightCenter.x - HORIZONTAL_SPACING / 2, targetY: rightCenter.y - VERTICAL_SPACING / 2 },
    { id: 5, label: LABELS[5], targetX: rightCenter.x + HORIZONTAL_SPACING / 2, targetY: rightCenter.y - VERTICAL_SPACING / 2 },
    { id: 6, label: LABELS[6], targetX: rightCenter.x, targetY: rightCenter.y + VERTICAL_SPACING / 2 },
  ];

  return rawSlots.map((slot) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const dx = slot.targetX - centerX;
    const dy = slot.targetY - centerY;
    const distance = Math.max(1, Math.hypot(dx, dy));

    if (distance >= 340) {
      return slot;
    }

    const push = 340 / distance;

    return {
      ...slot,
      targetX: centerX + dx * push,
      targetY: centerY + dy * push,
    };
  });
}

function createCell(slot: Slot, width: number, height: number): Cell {
  const start = spawnFromEdge(width, height);
  const departure = targetEdge(width, height);

  return {
    ...slot,
    activeUntil: 0,
    activationAt: performance.now() + randomBetween(4000, 8000),
    departAt: performance.now() + randomBetween(25000, 40000),
    departureX: departure.x,
    departureY: departure.y,
    lockStartedAt: 0,
    opacity: 0,
    phase: randomBetween(0, Math.PI * 2),
    speed: randomBetween(1.5, 2.5),
    state: "incoming",
    x: start.x,
    y: start.y,
  };
}

function createFloatingHex(width: number, height: number): FloatingHex {
  return {
    opacity: 0.06,
    phase: randomBetween(0, Math.PI * 2),
    size: randomBetween(14, 20),
    vx: randomBetween(0.1, 0.3) * (Math.random() > 0.5 ? 1 : -1),
    vy: randomBetween(0.1, 0.3) * (Math.random() > 0.5 ? 1 : -1),
    x: randomBetween(0, width),
    y: randomBetween(0, height),
  };
}

export default function HexGrid() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameRef = useRef<number | null>(null);
  const frameCountRef = useRef(0);
  const cellsRef = useRef<Cell[]>([]);
  const floatingHexesRef = useRef<FloatingHex[]>([]);
  const edgeParticlesRef = useRef<Map<string, EdgeParticle>>(new Map());
  const sizeRef = useRef({ dpr: 1, height: 0, width: 0 });
  const colorsRef = useRef({
    accentBright: "#E8B84B",
    accentGlow: "rgba(201,151,58,0.075)",
    accentPrimary: "#C9973A",
    edgeColor: "rgba(201,151,58,0.08)",
    nodeInactive: "rgba(201,151,58,0.25)",
  });

  const hydrateColors = useCallback(() => {
    colorsRef.current = {
      accentBright: cssVar("--accent-bright", "#E8B84B"),
      accentGlow: "rgba(201,151,58,0.075)",
      accentPrimary: cssVar("--accent-primary", "#C9973A"),
      edgeColor: "rgba(201,151,58,0.08)",
      nodeInactive: cssVar("--node-inactive", "rgba(201,151,58,0.25)"),
    };
  }, []);

  const initialiseScene = useCallback(() => {
    const { height, width } = sizeRef.current;
    const slots = buildSlots(width, height);

    cellsRef.current = slots.map((slot) => createCell(slot, width, height));
    floatingHexesRef.current = Array.from({ length: FLOATING_COUNT }, () => createFloatingHex(width, height));
    edgeParticlesRef.current = new Map(ADJACENCY.map(([from, to]) => [`${from}-${to}`, { direction: 1, progress: Math.random() }]));
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
    hydrateColors();
    initialiseScene();
  }, [hydrateColors, initialiseScene]);

  const updateCells = useCallback((now: number) => {
    const { height, width } = sizeRef.current;

    for (const floating of floatingHexesRef.current) {
      floating.x += floating.vx;
      floating.y += floating.vy;

      if (floating.x < -80) {
        floating.x = width + 80;
      } else if (floating.x > width + 80) {
        floating.x = -80;
      }

      if (floating.y < -80) {
        floating.y = height + 80;
      } else if (floating.y > height + 80) {
        floating.y = -80;
      }
    }

    for (const cell of cellsRef.current) {
      if (cell.state === "incoming") {
        const dx = cell.targetX - cell.x;
        const dy = cell.targetY - cell.y;
        const distance = Math.hypot(dx, dy);

        if (distance <= 8) {
          cell.x = cell.targetX;
          cell.y = cell.targetY;
          cell.opacity = 1;
          cell.lockStartedAt = now;
          cell.state = "locking";
          continue;
        }

        cell.x += (dx / distance) * cell.speed;
        cell.y += (dy / distance) * cell.speed;
        cell.opacity = Math.min(0.4, cell.opacity + 0.012);
      } else if (cell.state === "locking") {
        if (now - cell.lockStartedAt >= 400) {
          cell.state = "locked";
        }
      } else if (cell.state === "locked") {
        if (now >= cell.activationAt) {
          cell.activeUntil = now + randomBetween(1500, 2500);
          cell.state = "active";
        } else if (now >= cell.departAt) {
          const departure = targetEdge(width, height);
          cell.departureX = departure.x;
          cell.departureY = departure.y;
          cell.state = "departing";
        }
      } else if (cell.state === "active") {
        if (now >= cell.activeUntil) {
          cell.activationAt = now + randomBetween(4000, 8000);
          cell.state = "locked";
        }
      } else if (cell.state === "departing") {
        cell.x += (cell.departureX - cell.x) * 0.025;
        cell.y += (cell.departureY - cell.y) * 0.025;
        cell.opacity -= 1 / 60;

        if (cell.opacity <= 0) {
          const replacement = createCell(cell, width, height);
          Object.assign(cell, replacement);
        }
      }
    }
  }, []);

  const drawBackgroundGrid = useCallback((context: CanvasRenderingContext2D) => {
    const { height, width } = sizeRef.current;
    const horizontal = GRID_SIZE * 1.5;
    const vertical = GRID_SIZE * Math.sqrt(3);

    context.strokeStyle = "rgba(201,151,58,0.025)";
    context.lineWidth = 0.5;

    for (let row = -2; row < height / vertical + 4; row += 1) {
      for (let column = -2; column < width / horizontal + 4; column += 1) {
        const x = column * horizontal + (row % 2) * (horizontal / 2);
        const y = row * vertical;
        drawFlatHex(context, x, y, GRID_SIZE);
        context.stroke();
      }
    }
  }, []);

  const drawFloatingHexes = useCallback((context: CanvasRenderingContext2D, timestamp: number) => {
    const { accentPrimary } = colorsRef.current;

    for (const floating of floatingHexesRef.current) {
      context.save();
      context.translate(floating.x, floating.y);
      context.rotate(Math.sin(timestamp * 0.00025 + floating.phase) * 0.08);
      drawFlatHex(context, 0, 0, floating.size);
      context.strokeStyle = `rgba(201,151,58,${floating.opacity})`;
      context.lineWidth = 0.75;
      context.stroke();
      context.fillStyle = accentPrimary;
      context.globalAlpha = 0.015;
      context.fill();
      context.restore();
    }
  }, []);

  const drawEdges = useCallback((context: CanvasRenderingContext2D, timestamp: number) => {
    const cellsById = new Map(cellsRef.current.map((cell) => [cell.id, cell]));
    const { edgeColor } = colorsRef.current;

    for (const [fromId, toId] of ADJACENCY) {
      const from = cellsById.get(fromId);
      const to = cellsById.get(toId);

      if (!from || !to || from.state === "incoming" || to.state === "incoming" || from.state === "departing" || to.state === "departing") {
        continue;
      }

      const active = from.state === "active" || to.state === "active";
      context.beginPath();
      context.moveTo(from.targetX, from.targetY);
      context.lineTo(to.targetX, to.targetY);
      context.strokeStyle = active ? "rgba(201,151,58,0.35)" : edgeColor;
      context.lineWidth = active ? 1 : 0.5;
      context.stroke();

      if (active) {
        const particleKey = `${fromId}-${toId}`;
        const particle = edgeParticlesRef.current.get(particleKey) ?? { direction: 1, progress: 0 };
        particle.progress += (1 / 90) * particle.direction;

        if (particle.progress >= 1 || particle.progress <= 0) {
          particle.direction = particle.direction === 1 ? -1 : 1;
          particle.progress = Math.max(0, Math.min(1, particle.progress));
        }

        edgeParticlesRef.current.set(particleKey, particle);

        const eased = 0.5 - Math.cos(particle.progress * Math.PI) / 2;
        const x = from.targetX + (to.targetX - from.targetX) * eased;
        const y = from.targetY + (to.targetY - from.targetY) * eased;

        context.beginPath();
        context.fillStyle = "rgba(232,184,75,0.65)";
        context.arc(x, y, 2 + Math.sin(timestamp * 0.008) * 0.35, 0, Math.PI * 2);
        context.fill();
        context.beginPath();
        context.fillStyle = "rgba(201,151,58,0.10)";
        context.arc(x, y, 7, 0, Math.PI * 2);
        context.fill();
      }
    }
  }, []);

  const drawCells = useCallback((context: CanvasRenderingContext2D, timestamp: number) => {
    const { accentGlow, nodeInactive } = colorsRef.current;

    context.textAlign = "center";
    context.textBaseline = "middle";
    context.font = `11px ${getComputedStyle(document.body).fontFamily}`;

    for (const cell of cellsRef.current) {
      const pulse = Math.sin(timestamp * 0.0019 + cell.phase) * 0.025;
      const active = cell.state === "active";

      if (cell.state === "locking") {
        const progress = Math.min(1, (timestamp - cell.lockStartedAt) / 400);

        context.beginPath();
        context.arc(cell.targetX, cell.targetY, HEX_SIZE + progress * 32, 0, Math.PI * 2);
        context.strokeStyle = `rgba(201,151,58,${0.3 * (1 - progress)})`;
        context.lineWidth = 1 + progress * 3;
        context.stroke();
      }

      if (active) {
        context.beginPath();
        context.arc(cell.targetX, cell.targetY, 50, 0, Math.PI * 2);
        context.strokeStyle = accentGlow;
        context.lineWidth = 8;
        context.stroke();
      }

      drawFlatHex(context, cell.x, cell.y, HEX_SIZE);

      if (cell.state === "incoming") {
        context.strokeStyle = `rgba(201,151,58,${cell.opacity})`;
        context.lineWidth = 1;
        context.stroke();
        continue;
      }

      if (cell.state === "departing") {
        context.globalAlpha = Math.max(0, cell.opacity);
      }

      context.fillStyle = active ? "rgba(201,151,58,0.10)" : `rgba(201,151,58,${0.05 + pulse})`;
      context.strokeStyle = active ? "rgba(232,184,75,0.50)" : nodeInactive.replace("0.25", `${0.2 + pulse}`);
      context.lineWidth = active ? 2 : 1.5;
      context.fill();
      context.stroke();

      context.fillStyle = active ? "rgba(232,184,75,0.60)" : `rgba(201,151,58,${0.35 + pulse})`;
      context.fillText(cell.label, cell.x, cell.y);
      context.globalAlpha = 1;
    }
  }, []);

  const draw = useCallback(
    (timestamp: number) => {
      const canvas = canvasRef.current;
      const context = canvas?.getContext("2d");

      if (!canvas || !context) {
        return;
      }

      frameCountRef.current += 1;

      if (frameCountRef.current % 2 === 0) {
        updateCells(timestamp);
      }

      const { dpr, height, width } = sizeRef.current;
      const formationCenterX = width * 0.5;
      const formationCenterY = height * 0.48;
      const scale = 1 + Math.sin(timestamp * 0.0008) * 0.015;

      context.clearRect(0, 0, canvas.width, canvas.height);
      context.save();
      context.scale(dpr, dpr);

      drawBackgroundGrid(context);
      drawFloatingHexes(context, timestamp);

      context.save();
      context.translate(formationCenterX, formationCenterY);
      context.scale(scale, scale);
      context.translate(-formationCenterX, -formationCenterY);
      drawEdges(context, timestamp);
      drawCells(context, timestamp);
      context.restore();

      context.save();
      context.globalCompositeOperation = "destination-out";
      const mask = context.createRadialGradient(width / 2, height * 0.45, 60, width / 2, height * 0.45, 320);
      mask.addColorStop(0, "rgba(0,0,0,0.85)");
      mask.addColorStop(0.5, "rgba(0,0,0,0.4)");
      mask.addColorStop(1, "rgba(0,0,0,0)");
      context.fillStyle = mask;
      context.fillRect(0, 0, width, height);
      context.restore();

      context.restore();
      frameRef.current = requestAnimationFrame(draw);
    },
    [drawBackgroundGrid, drawCells, drawEdges, drawFloatingHexes, updateCells],
  );

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return undefined;
    }

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
  }, [draw, resizeCanvas]);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none absolute inset-0 z-0 h-full w-full" />;
}
