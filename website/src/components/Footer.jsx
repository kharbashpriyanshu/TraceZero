import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.brand}>
          <span className={styles.icon}>⚡</span>
          Trace<strong>Zero</strong>
          <span className={styles.version}>v1.0.0</span>
        </div>
        <div className={styles.links}>
          <a href="https://github.com/kharbashpriyanshu/TraceZero" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://github.com/kharbashpriyanshu/TraceZero/issues" target="_blank" rel="noreferrer">Report Bug</a>
          <a href="https://github.com/kharbashpriyanshu/TraceZero/blob/main/README.md" target="_blank" rel="noreferrer">Docs</a>
        </div>
        <div className={styles.copy}>MIT License © 2025 TraceZero</div>
      </div>
    </footer>
  )
}
