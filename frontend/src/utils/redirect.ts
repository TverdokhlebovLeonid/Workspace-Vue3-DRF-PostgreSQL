export function sanitizeRedirectPath(value: unknown, fallback = '/schedule'): string {
  if (typeof value !== 'string' || !value) {
    return fallback
  }
  if (!value.startsWith('/') || value.startsWith('//') || value.includes('://')) {
    return fallback
  }
  return value
}
