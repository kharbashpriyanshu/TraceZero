import { useEffect, useRef } from 'react'
import styles from './Features.module.css'

const FEATURES = [
  { icon: '🗂️', color: 'blue',   title: 'Deep File Scanner',          desc: 'Crawls Program Files, AppData Local/Roaming/LocalLow, ProgramData, and Temp folders to find every leftover file.' },
  { icon: '🔑', color: 'purple', title: 'Registry Cleaner',           desc: 'Detects orphaned registry keys under HKLM and HKCU Uninstall paths left by removed software.' },
  { icon: '🛡️', color: 'green',  title: 'Risk Analyzer',              desc: 'Every item is classified as Safe, Review, or Risky before you delete anything.' },
  { icon: '📦', color: 'orange', title: 'Package Manager Detection',  desc: 'Identifies traces from Chocolatey, Winget, Scoop and other package managers so nothing slips through.' },
  { icon: '🔗', color: 'blue',   title: 'Orphan Shortcut Cleanup',    desc: 'Finds broken Desktop and Start Menu shortcuts pointing to programs that no longer exist.' },
  { icon: '🗑️', color: 'green',  title: 'Safe Recycle Bin',           desc: 'All deletions go to a managed recycle bin with full history logging — never a permanent accident.' },
  { icon: '📊', color: 'purple', title: 'Scan History & DB',          desc: 'Every scan session is recorded in a local SQLite database so you can review what was cleaned and when.' },
  { icon: '⚡', color: 'orange', title: 'Multi-threaded Scanning',    desc: 'Uses up to 4 parallel threads to scan your system fast without freezing the UI or hogging CPU.' },
]

export default function Features() {
  const cardRefs = useRef([])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles.visible)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.12 }
    )
    cardRefs.current.forEach(el => el && observer.observe(el))
    return () => observer.disconnect()
  }, [])

  return (
    <section className={styles.section} id="features">
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.eyebrow}>Features</div>
          <h2>Everything Your PC Needs to Stay Clean</h2>
          <p>TraceZero goes beyond a simple uninstaller — it's a forensic trace hunter.</p>
        </header>

        <div className={styles.grid}>
          {FEATURES.map((f, i) => (
            <div
              key={i}
              className={styles.card}
              ref={el => (cardRefs.current[i] = el)}
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className={`${styles.icon} ${styles[f.color]}`}>{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
