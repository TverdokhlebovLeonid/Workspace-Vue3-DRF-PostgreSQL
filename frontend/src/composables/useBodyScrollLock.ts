let lockCount = 0
let savedBodyPaddingRight = ''
function getScrollbarWidth() {
  return Math.max(0, window.innerWidth - document.documentElement.clientWidth)
}
export function lockBodyScroll() {
  if (lockCount === 0) {
    const scrollbarWidth = getScrollbarWidth()
    savedBodyPaddingRight = document.body.style.paddingRight
    if (scrollbarWidth) {
      document.body.style.paddingRight = `${scrollbarWidth}px`
      document.documentElement.style.setProperty('--scrollbar-compensate', `${scrollbarWidth}px`)
    }
    document.body.classList.add('modal-open')
  }
  lockCount++
}
export function unlockBodyScroll() {
  lockCount = Math.max(0, lockCount - 1)
  if (lockCount === 0) {
    document.body.classList.remove('modal-open')
    document.body.style.paddingRight = savedBodyPaddingRight
    document.documentElement.style.removeProperty('--scrollbar-compensate')
  }
}
