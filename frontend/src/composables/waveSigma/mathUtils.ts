// Simple pseudo-random noise generator
export const fract = (x: number): number => x - Math.floor(x)
export const mix = (a: number, b: number, t: number): number => a * (1 - t) + b * t

// 1D Noise
export const hash = (n: number): number => {
  return fract(Math.sin(n) * 43758.5453)
}

export const noise = (x: number): number => {
  const i = Math.floor(x)
  const f = fract(x)
  const u = f * f * (3 - 2 * f)
  return mix(hash(i), hash(i + 1), u)
}

// Color ramp function (Blue -> Cyan -> Green -> Yellow -> Red)
export const getHeatmapColor = (t: number, out: { r: number; g: number; b: number }): void => {
  // Normalize t roughly between 0 and 1
  const val = Math.max(0, Math.min(1, t))

  if (val < 0.25) {
    // Blue to Cyan
    const p = val / 0.25
    out.r = 0
    out.g = p
    out.b = 1
  } else if (val < 0.5) {
    // Cyan to Green
    const p = (val - 0.25) / 0.25
    out.r = 0
    out.g = 1
    out.b = 1 - p
  } else if (val < 0.75) {
    // Green to Yellow
    const p = (val - 0.5) / 0.25
    out.r = p
    out.g = 1
    out.b = 0
  } else {
    // Yellow to Red
    const p = (val - 0.75) / 0.25
    out.r = 1
    out.g = 1 - p
    out.b = 0
  }
}
