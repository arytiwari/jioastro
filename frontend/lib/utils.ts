type ClassValue =
  | string
  | number
  | null
  | undefined
  | boolean
  | ClassValue[]
  | { [key: string]: boolean | undefined | null }

function pushClass(acc: string[], value: ClassValue): void {
  if (!value && value !== 0) {
    return
  }

  if (typeof value === "string" || typeof value === "number") {
    acc.push(String(value))
    return
  }

  if (Array.isArray(value)) {
    value.forEach((item) => pushClass(acc, item))
    return
  }

  if (typeof value === "object") {
    for (const [key, active] of Object.entries(value)) {
      if (active) {
        acc.push(key)
      }
    }
  }
}

export function cn(...inputs: ClassValue[]): string {
  const classes: string[] = []
  inputs.forEach((input) => pushClass(classes, input))
  return classes.join(" ").trim()
}

function toDate(value: string | Date | null | undefined): Date | null {
  if (!value) {
    return null
  }

  const date = typeof value === "string" ? new Date(value) : value
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(value: string | Date | null | undefined): string {
  const date = toDate(value)
  if (!date) {
    return ""
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export function formatTime(value: string | Date | null | undefined): string {
  const date = toDate(value)
  if (!date) {
    return ""
  }

  return date.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  })
}
