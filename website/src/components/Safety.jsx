import styles from './Safety.module.css'

const FORBIDDEN = [
  { path: 'C:\\Windows & all subdirectories', icon: '🔒' },
  { path: 'C:\\Windows\\System32 & SysWOW64', icon: '🔒' },
  { path: 'C:\\Recovery, C:\\Boot, C:\\EFI',   icon: '🔒' },
  { path: 'C:\\$Recycle.Bin & System Volume',  icon: '🔒' },
  { path: '.NET, DirectX, VC++ Runtimes, Drivers', icon: '🔒' },
  { path: 'Windows Defender & Windows Update', icon: '🔒' },
]

const PROTECTED = [
  'System32', 'Windows Update', '.NET Runtime',
  'Drivers', 'EFI / Boot', 'Recycle Bin',
]

export default function Safety() {
  return (
    <section className={styles.section} id="safety">
      <div className={styles.container}>
        <div className={styles.inner}>
          {/* text side */}
          <div className={styles.text}>
            <div className={styles.eyebrow}>Safety First</div>
            <h2>Protected by Design</h2>
            <p>
              TraceZero has a strict forbidden zone list built into its core.
              It will <strong>never touch</strong> any of the following, no matter what:
            </p>
            <ul className={styles.list}>
              {FORBIDDEN.map((f, i) => (
                <li key={i}>
                  {f.icon} <code>{f.path}</code>
                </li>
              ))}
            </ul>
          </div>

          {/* card side */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.pulseDot} />
              Protection Status
            </div>
            <div className={styles.rows}>
              {PROTECTED.map((p, i) => (
                <div key={i} className={styles.row}>
                  <span>{p}</span>
                  <span className={styles.ok}>✔ Protected</span>
                </div>
              ))}
            </div>
            <div className={styles.cardFooter}>
              All deletions are reversible via the built-in history log.
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
