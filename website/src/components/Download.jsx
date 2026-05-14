import styles from './Download.module.css'

export default function Download() {
  return (
    <section className={styles.section} id="download">
      <div className={styles.glow} />
      <div className={styles.container}>
        <h2>Ready to Clean Your PC?</h2>
        <p>Free, open-source, and always will be. No telemetry. No ads. Just clean.</p>

        <div className={styles.buttons}>
          <a
            href="https://github.com/kharbashpriyanshu/TraceZero/releases"
            target="_blank" rel="noreferrer"
            className={`${styles.btn} ${styles.primary}`}
            id="btn-download-exe"
          >
            <DownloadIcon /> Download .exe (Windows)
          </a>
          <a
            href="https://github.com/kharbashpriyanshu/TraceZero"
            target="_blank" rel="noreferrer"
            className={`${styles.btn} ${styles.ghost}`}
            id="btn-github"
          >
            <GithubIcon /> Clone from GitHub
          </a>
        </div>

        <div className={styles.meta}>
          🪟 Windows 10 / 11 &nbsp;·&nbsp; Python 3.10+ required for source &nbsp;·&nbsp; MIT License
        </div>

        <div className={styles.codeWrap}>
          <div className={styles.codeLabel}>Or run from source:</div>
          <pre className={styles.code}>
            <span className={styles.comment}>{`# Clone the repo`}</span>{'\n'}
            {`git clone https://github.com/kharbashpriyanshu/TraceZero.git\ncd TraceZero`}{'\n'}
            <span className={styles.comment}>{`# Install dependencies`}</span>{'\n'}
            {`pip install -r requirements.txt`}{'\n'}
            <span className={styles.comment}>{`# Launch`}</span>{'\n'}
            {`python main.py`}
          </pre>
        </div>
      </div>
    </section>
  )
}

function DownloadIcon() {
  return (
    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
    </svg>
  )
}
function GithubIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.744 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
    </svg>
  )
}
