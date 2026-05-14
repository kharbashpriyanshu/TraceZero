import { useState, useEffect } from 'react'
import styles from './Navbar.module.css'

import logoImg from '../assets/logo.png'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const links = ['Features', 'How It Works', 'Safety', 'Download']

  return (
    <nav className={`${styles.nav} ${scrolled ? styles.scrolled : ''}`}>
      <div className={styles.inner}>
        <a href="#" className={styles.logo}>
          <img src={logoImg} alt="TraceZero Logo" className={styles.logoImg} style={{ height: '32px', width: 'auto' }} />
        </a>

        <ul className={styles.links}>
          {links.map(l => (
            <li key={l}>
              <a href={`#${l.toLowerCase().replace(/ /g, '-')}`}>{l}</a>
            </li>
          ))}
        </ul>

        <a href="#download" className={`${styles.cta} ${styles.btnPrimary}`}>
          Download Free
        </a>

        <button
          className={`${styles.hamburger} ${menuOpen ? styles.open : ''}`}
          onClick={() => setMenuOpen(p => !p)}
          aria-label="Toggle menu"
        >
          <span /><span /><span />
        </button>
      </div>

      {menuOpen && (
        <div className={styles.mobileMenu}>
          {links.map(l => (
            <a
              key={l}
              href={`#${l.toLowerCase().replace(/ /g, '-')}`}
              onClick={() => setMenuOpen(false)}
            >
              {l}
            </a>
          ))}
        </div>
      )}
    </nav>
  )
}
