import { useEffect, useRef } from 'react'
import styles from './HowItWorks.module.css'

const STEPS = [
  {
    num: '01', icon: '🔍', title: 'Scan',
    desc: 'Click Start Scan. TraceZero deep-scans your file system, registry, and package manager records simultaneously across 4 threads.',
  },
  {
    num: '02', icon: '🎯', title: 'Review',
    desc: 'Every trace is listed with size, location, and risk level. Expand any item to see the full path before making a decision.',
  },
  {
    num: '03', icon: '✅', title: 'Remove',
    desc: 'Select what to delete and hit Clean Selected. Items go to a managed recycle bin — always recoverable from the history log.',
  },
]

export default function HowItWorks() {
  const stepRefs = useRef([])

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add(styles.visible)
            observer.unobserve(e.target)
          }
        })
      },
      { threshold: 0.15 }
    )
    stepRefs.current.forEach(el => el && observer.observe(el))
    return () => observer.disconnect()
  }, [])

  return (
    <section className={styles.section} id="how-it-works">
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.eyebrow}>How It Works</div>
          <h2>Clean in Three Simple Steps</h2>
          <p>No configuration needed. Just scan, review, and remove.</p>
        </header>

        <div className={styles.stepsRow}>
          {STEPS.map((s, i) => (
            <>
              <div
                key={s.num}
                className={styles.step}
                ref={el => (stepRefs.current[i] = el)}
                style={{ animationDelay: `${i * 120}ms` }}
              >
                <div className={styles.stepNum}>{s.num}</div>
                <div className={styles.stepIcon}>{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
              {i < STEPS.length - 1 && (
                <div key={`arrow-${i}`} className={styles.arrow}>→</div>
              )}
            </>
          ))}
        </div>
      </div>
    </section>
  )
}
