import { ref, watchEffect } from 'vue'

type ThemeMode = 'dark' | 'light' | 'auto'
type ResolvedTheme = 'dark' | 'light'

const STORAGE_KEY = 'blog-theme'

/* ── Sunrise / Sunset ───────────────────────
   Crude but effective: uses a fixed solar equation
   with the user's local latitude approximated by
   JS Date timezone offset. Good enough for a blog.
   ──────────────────────────────────────────── */

function getSunTimes(now: Date): { sunrise: Date; sunset: Date } {
  const start = new Date(now.getFullYear(), 0, 0)
  const diff = now.getTime() - start.getTime()
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24))

  // Solar declination (radians)
  const declination = 23.45 * Math.sin((2 * Math.PI / 365) * (dayOfYear - 81)) * (Math.PI / 180)

  // Use a mid-latitude (45°N) as default — covers most users reasonably
  const latitude = 45 * (Math.PI / 180)

  // Hour angle at sunrise/sunset
  const cosHourAngle = (Math.sin(-0.83 * (Math.PI / 180)) - Math.sin(latitude) * Math.sin(declination))
    / (Math.cos(latitude) * Math.cos(declination))

  // Clamp for polar regions
  const clampedCos = Math.max(-1, Math.min(1, cosHourAngle))
  const hourAngle = Math.acos(clampedCos) * (180 / Math.PI)

  // Solar noon ≈ 12:00 local (ignoring equation of time, ~few min error)
  const sunriseHour = 12 - hourAngle / 15
  const sunsetHour = 12 + hourAngle / 15

  const sunrise = new Date(now)
  sunrise.setHours(Math.floor(sunriseHour), Math.round((sunriseHour % 1) * 60), 0, 0)

  const sunset = new Date(now)
  sunset.setHours(Math.floor(sunsetHour), Math.round((sunsetHour % 1) * 60), 0, 0)

  return { sunrise, sunset }
}

function resolveFromTime(): ResolvedTheme {
  const now = new Date()
  const { sunrise, sunset } = getSunTimes(now)
  return (now >= sunrise && now < sunset) ? 'light' : 'dark'
}

/* ── Resolve the initial theme (SSR-safe) ─── */

function getInitialMode(): ThemeMode {
  try {
    return (localStorage.getItem(STORAGE_KEY) as ThemeMode) || 'auto'
  } catch {
    return 'auto'
  }
}

function resolveInitialTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === 'auto') return resolveFromTime()
  return mode
}

const mode = ref<ThemeMode>(getInitialMode())
const theme = ref<ResolvedTheme>(resolveInitialTheme(mode.value))

let timer: ReturnType<typeof setTimeout> | null = null

function applyTheme(t: ResolvedTheme) {
  try {
    document.documentElement.setAttribute('data-theme', t)
  } catch {
    // SSR guard
  }
}

/* ── Auto-switch timer ────────────────────── */

function scheduleNextCheck() {
  if (timer) clearTimeout(timer)
  if (mode.value !== 'auto') return

  // Re-resolve every minute so auto mode tracks sunrise/sunset
  timer = setTimeout(() => {
    if (mode.value === 'auto') {
      theme.value = resolveFromTime()
    }
    scheduleNextCheck()
  }, 60_000) // 1 minute
}

/* ── Persistence & reactive apply ─────────── */

watchEffect(() => {
  // Resolve the actual theme from the current mode
  if (mode.value === 'auto') {
    theme.value = resolveFromTime()
  } else {
    theme.value = mode.value
  }

  applyTheme(theme.value)

  try {
    localStorage.setItem(STORAGE_KEY, mode.value)
  } catch {
    // SSR guard
  }

  // (Re)schedule the auto-check timer
  scheduleNextCheck()
})

export function useTheme() {
  /** Manual toggle: cycles dark → light → auto */
  function toggle(event?: MouseEvent) {
    // View Transitions API: circular reveal from click point
    const doToggle = () => {
      if (mode.value === 'dark') mode.value = 'light'
      else if (mode.value === 'light') mode.value = 'auto'
      else mode.value = 'dark'
    }

    // Check support + not auto mode (auto doesn't need fancy animation)
    if (
      mode.value === 'auto' ||
      typeof document === 'undefined' ||
      !document.startViewTransition
    ) {
      doToggle()
      return
    }

    // Get click coordinates (fallback to center)
    const x = event?.clientX ?? window.innerWidth / 2
    const y = event?.clientY ?? window.innerHeight / 2

    // Calculate the max radius needed to cover the screen
    const endRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
    )

    const transition = document.startViewTransition(() => doToggle())

    transition.ready.then(() => {
      const root = document.documentElement
      const isDarkToLight = mode.value === 'light'
      root.animate(
        {
          clipPath: isDarkToLight
            ? [`circle(0 at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`]
            : [`circle(${endRadius}px at ${x}px ${y}px)`, `circle(0 at ${x}px ${y}px)`],
        },
        {
          duration: 200,
          easing: 'ease-out',
          pseudoElement: '::view-transition-new(root)',
        }
      )
    }).catch(() => {
      // Transition interrupted — no-op, theme already applied
    })
  }

  /** Cycle label for the toggle button */
  function cycleLabel(): string {
    if (mode.value === 'dark') return 'dark'
    if (mode.value === 'light') return 'light'
    return 'auto'
  }

  return { theme, mode, toggle, cycleLabel }
}
