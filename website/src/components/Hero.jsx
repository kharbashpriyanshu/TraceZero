import { useState, useEffect, useRef } from 'react'
import styles from './Hero.module.css'

const PREVIEW_ROWS = [
  { name: 'Discord Leftovers',     size: '340 MB', risk: 'safe' },
  { name: 'Adobe Registry Keys',   size: '12 KB',  risk: 'review' },
  { name: 'Unknown AppData Cache', size: '890 MB', risk: 'risky' },
  { name: 'Spotify Temp Files',    size: '68 MB',  risk: 'safe' },
  { name: 'Epic Games Residuals',  size: '1.2 GB', risk: 'review' },
]

function useCounter(target, duration = 1800, start = false) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!start) return
    let startTime = null
    const step = (ts) => {
      if (!startTime) startTime = ts
      const p = Math.min((ts - startTime) / duration, 1)
      setVal(Math.floor(p * target))
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [start, target, duration])
  return val
}

export default function Hero() {
  const previewRef = useRef(null)
  const statsRef   = useRef(null)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [statsVisible,   setStatsVisible]   = useState(false)

  useEffect(() => {
    const obs1 = new IntersectionObserver(([e]) => { if (e.isIntersecting) setPreviewVisible(true) }, { threshold: 0.05 })
    const obs2 = new IntersectionObserver(([e]) => { if (e.isIntersecting) setStatsVisible(true)   }, { threshold: 0.1  })
    if (previewRef.current) obs1.observe(previewRef.current)
    if (statsRef.current)   obs2.observe(statsRef.current)
    return () => { obs1.disconnect(); obs2.disconnect() }
  }, [])

  const c1 = useCounter(6,  1400, statsVisible)
  const c2 = useCounter(247, 1600, statsVisible)
  const c3 = useCounter(100, 1200, statsVisible)

  return (
    <section className={styles.hero} id="hero">
      {/* animated mesh bg */}
      <div className={styles.meshBg} />
      <div className={styles.noiseOverlay} />
      <div className={`${styles.orb} ${styles.orb1}`} />
      <div className={`${styles.orb} ${styles.orb2}`} />
      <div className={`${styles.orb} ${styles.orb3}`} />

      <div className={styles.container}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          <span>v1.0.0</span>
          <span className={styles.badgeSep}>·</span>
          <span>Free &amp; Open Source</span>
          <span className={styles.badgeSep}>·</span>
          <span>Windows 10/11</span>
        </div>

        <h1 className={styles.title}>
          Leave&nbsp;<span className={styles.gradient}>Zero&nbsp;Traces</span>
          <br />Behind Uninstalled&nbsp;Apps
        </h1>

        <p className={styles.sub}>
          TraceZero forensically hunts leftover files, registry keys, AppData folders,
          and orphaned shortcuts — then safely removes them so Windows stays fast and clean.
        </p>

        <div className={styles.actions}>
          <a href="#download" className={styles.btnPrimary}>
            <DownloadIcon />
            Download for Windows
          </a>
          <a href="https://github.com/kharbashpriyanshu/TraceZero" target="_blank" rel="noreferrer" className={styles.btnGhost}>
            <GithubIcon />
            View on GitHub
          </a>
        </div>

        {/* animated counters */}
        <div className={styles.stats} ref={statsRef}>
          <Stat num={`${c1}+`}  label="Scan Locations"   delay="0ms" />
          <div className={styles.statDiv} />
          <Stat num={`${c2}`}   label="Apps Detected"    delay="100ms" />
          <div className={styles.statDiv} />
          <Stat num={`${c3}%`}  label="Safe by Design"   delay="200ms" />
          <div className={styles.statDiv} />
          <Stat num="Free"      label="Always"            delay="300ms" />
        </div>
      </div>

      {/* ── App window preview ── */}
      <div className={`${styles.preview} ${styles.container} ${previewVisible ? styles.previewVisible : ''}`} ref={previewRef}>
        <div className={styles.glowRing} />
        <div className={styles.window}>
          <div className={styles.titlebar}>
            <div className={styles.dots}>
              <span className={`${styles.dot} ${styles.dotRed}`} />
              <span className={`${styles.dot} ${styles.dotYellow}`} />
              <span className={`${styles.dot} ${styles.dotGreen}`} />
            </div>
            <span className={styles.winTitle}>TraceZero  v1.0.0</span>
            <span className={styles.winBadge}>🛡 Safe by Design</span>
          </div>
          <div className={styles.winBody}>
            {/* sidebar */}
            <aside className={styles.sidebar}>
              <div className={styles.sideHeader}>
                <span className={styles.sideIcon}>⚡</span>
                <div>
                  <div className={styles.sideAppName}>TraceZero</div>
                  <div className={styles.sideAppSub}>Smart trace cleaner</div>
                </div>
              </div>
              {[
                { icon: '⚡', label: 'Dashboard', active: true },
                { icon: '🔍', label: 'Scan & Clean' },
                { icon: '📋', label: 'History' },
                { icon: '⚙️', label: 'Settings' },
              ].map((item, i) => (
                <div key={i} className={`${styles.sideItem} ${item.active ? styles.sideActive : ''}`}>
                  <span>{item.icon}</span> {item.label}
                </div>
              ))}
              <div className={styles.sideSafeTag}>✔ Safe by Design</div>
            </aside>

            {/* main */}
            <div className={styles.mainPane}>
              <div className={styles.mainHeader}>
                <div>
                  <div className={styles.welcomeText}>Welcome to</div>
                  <div className={styles.appTitle}>TraceZero ⚡</div>
                  <div className={styles.appSub}>Detect and safely remove leftover application traces from Windows</div>
                </div>
                <button className={styles.scanBtn}>⚡ Start Scan</button>
              </div>

              <div className={styles.statCards}>
                {[
                  { label: 'Total Scans',   val: '1',      icon: '📊', color: 'blue'   },
                  { label: 'Items Found',   val: '0',      icon: '🗑️', color: 'yellow' },
                  { label: 'Space Freed',   val: '1.4 GB', icon: '💾', color: 'green'  },
                  { label: 'Items Cleaned', val: '0',      icon: '✅', color: 'red'    },
                ].map((c, i) => (
                  <div key={i} className={`${styles.statCard} ${styles[c.color]}`}>
                    <span className={styles.scIcon}>{c.icon}</span>
                    <div className={styles.scVal}>{c.val}</div>
                    <div className={styles.scLabel}>{c.label}</div>
                  </div>
                ))}
              </div>

              <div className={styles.listLabel}>What TraceZero Does</div>
              <div className={styles.featureGrid}>
                {[
                  { icon: '🔍', name: 'Deep Filesystem Scan',    sub: 'Scans AppData, Program Files, Temp & more' },
                  { icon: '🔑', name: 'Registry Analysis',       sub: 'Detects orphaned registry keys' },
                  { icon: '🔗', name: 'Dead Shortcut Finder',    sub: 'Finds broken .lnk files' },
                  { icon: '🛡️', name: 'Smart Risk Classification',sub: 'Labels every item Safe/Review/Risky' },
                  { icon: '🗑️', name: 'Recycle Bin Protection',  sub: 'All deletions are recoverable' },
                  { icon: '🎮', name: 'Game Store Detection',    sub: 'Steam, Epic, Winget & Chocolatey' },
                ].map((f, i) => (
                  <div key={i} className={styles.featureItem}>
                    <span className={styles.fiIcon}>{f.icon}</span>
                    <div>
                      <div className={styles.fiName}>{f.name}</div>
                      <div className={styles.fiSub}>{f.sub}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Stat({ num, label, delay }) {
  return (
    <div className={styles.stat} style={{ animationDelay: delay }}>
      <span className={styles.statNum}>{num}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  )
}

function DownloadIcon() {
  return (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
    </svg>
  )
}
function GithubIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.744 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
    </svg>
  )
}
