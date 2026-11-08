const slides = [...document.querySelectorAll('.slide')]
let current = 0

function show (i) {
  current = Math.max(0, Math.min(slides.length - 1, i))
  slides.forEach((s, j) => s.classList.toggle('on', j === current))
}

function fit () {
  document.body.style.setProperty('--scale', Math.min(innerWidth / 1920, innerHeight / 1080))
}

addEventListener('resize', fit)
addEventListener('keydown', event => {
  const present = document.body.classList.contains('present')
  if (event.key === 'f' || event.key === 'F') {
    document.body.classList.toggle('present')
    fit()
    show(current)
  } else if (present && ['ArrowRight', 'ArrowDown', ' ', 'PageDown'].includes(event.key)) {
    show(current + 1)
  } else if (present && ['ArrowLeft', 'ArrowUp', 'PageUp'].includes(event.key)) {
    show(current - 1)
  } else if (present && event.key === 'Escape') {
    document.body.classList.remove('present')
  }
})
