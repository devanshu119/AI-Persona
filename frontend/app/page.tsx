import ChatWidget from "./components/ChatWidget";
import BookingSection from "./components/BookingSection";

const CALCOM_USERNAME = process.env.NEXT_PUBLIC_CALCOM_USERNAME || "devanshu";

const SKILLS = [
  {
    icon: "🧠",
    title: "LLM & RAG Systems",
    tags: ["LangChain", "LLM APIs", "Ollama", "Prompt Engineering", "Vector Stores"],
  },
  {
    icon: "🔬",
    title: "ML / Deep Learning",
    tags: ["PyTorch", "TensorFlow", "Keras", "Scikit-learn", "OpenCV"],
  },
  {
    icon: "⚡",
    title: "Backend & APIs",
    tags: ["FastAPI", "Python", "Node.js", "Next.js", "Streamlit"],
  },
  {
    icon: "🚀",
    title: "MLOps & Cloud",
    tags: ["CI/CD", "GitHub Actions", "Docker", "AWS", "Model Fine-tuning"],
  },
  {
    icon: "📊",
    title: "Data & Analysis",
    tags: ["Pandas", "NumPy", "Matplotlib", "SQL", "Jupyter"],
  },
  {
    icon: "🏆",
    title: "Competitive Programming",
    tags: ["500+ DSA", "LeetCode", "Codeforces 1300+", "ICPC Style"],
  },
];

const PROJECTS = [
  {
    name: "VSCode Coding Assistant",
    company: "Planto.ai",
    desc: "Production LLM-powered coding assistant deployed to 3 enterprise clients. Reduced developer context-switching by ~30%.",
    tags: ["LangChain", "Ollama", "RAG", "CI/CD"],
    stat: "3 enterprise clients",
    color: "var(--accent-primary)",
  },
  {
    name: "Oil Spill Detection",
    company: "Computer Vision Project",
    desc: "U-Net, DeepLabv3, CNN models on SAR satellite imagery. Achieved >90% IoU, deployed via Streamlit.",
    tags: ["PyTorch", "OpenCV", "U-Net", "Streamlit"],
    stat: ">90% IoU",
    color: "var(--accent-cyan)",
  },
  {
    name: "Stock Volatility Forecasting",
    company: "Deep Learning Project",
    desc: "LSTM/GRU pipeline outperforming GARCH baseline by 18% on MAE. Garman-Klass, Bollinger Bands, RSI features.",
    tags: ["TensorFlow", "Keras", "LSTM", "GRU"],
    stat: "18% over GARCH",
    color: "var(--accent-emerald)",
  },
];

export default function Home() {
  return (
    <main>
      {/* ── Hero ─────────────────────────────────────── */}
      <section className="hero" id="hero">
        <div className="hero-bg">
          <div className="hero-grid" />
          <div className="hero-orb hero-orb-1" />
          <div className="hero-orb hero-orb-2" />
          <div className="hero-orb hero-orb-3" />
        </div>

        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            AI Persona · Live Chat & Booking
          </div>

          <h1 className="hero-title">
            Hi, I&apos;m{" "}
            <span className="hero-title-gradient">Devanshu&apos;s</span>
            <br />
            AI Representative
          </h1>

          <p className="hero-subtitle">
            Pre-final year CSE at IIIT Una. Specialising in LLM systems, RAG pipelines &amp; MLOps.
            Shipped production AI to enterprise clients. Ask me anything — or book a meeting directly.
          </p>

          <div className="hero-tags">
            <span className="tag tag-purple">LLM Systems</span>
            <span className="tag tag-cyan">RAG Pipelines</span>
            <span className="tag tag-emerald">MLOps</span>
            <span className="tag tag-pink">Planto.ai Intern</span>
            <span className="tag tag-purple">IIIT Una · 2027</span>
            <span className="tag tag-cyan">Codeforces 1300+</span>
          </div>

          <div className="hero-ctas">
            <a href="#chat" className="btn btn-primary" id="hero-chat-btn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z" />
              </svg>
              Chat with AI Persona
            </a>
            <a href="#voice" className="btn btn-secondary" id="hero-voice-btn">
              📞 Call the Voice Agent
            </a>
            <a href="#book" className="btn btn-secondary" id="hero-book-btn">
              📅 Book a Meeting
            </a>
          </div>
        </div>

        {/* Stats */}
        <div className="stats-strip">
          <div className="stat-item">
            <div className="stat-value">3</div>
            <div className="stat-label">Enterprise Clients</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">~25%</div>
            <div className="stat-label">Hallucination Reduction</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">500+</div>
            <div className="stat-label">DSA Problems</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">15%</div>
            <div className="stat-label">LLM Accuracy Gain</div>
          </div>
        </div>
      </section>

      {/* ── Chat Interface ─────────────────────────── */}
      <section id="chat" className="chat-section" style={{ paddingTop: "80px" }}>
        <div className="section-header">
          <div className="section-label">💬 Chat Interface</div>
          <h2 className="section-title">Ask Me Anything</h2>
          <p style={{ color: "var(--text-secondary)", marginTop: "12px", fontSize: "15px" }}>
            Every answer is grounded in Devanshu&apos;s actual resume and GitHub repos via RAG.
            No hardcoded strings. Try to probe it.
          </p>
        </div>
        <ChatWidget />
      </section>

      {/* ── Skills ────────────────────────────────── */}
      <section className="skills-section" id="skills">
        <div className="section-header">
          <div className="section-label">🛠 Technical Skills</div>
          <h2 className="section-title">Full-Stack AI Engineering</h2>
        </div>
        <div className="skills-grid">
          {SKILLS.map((skill) => (
            <div key={skill.title} className="skill-card" id={`skill-${skill.title.toLowerCase().replace(/\s+/g, "-")}`}>
              <div className="skill-icon">{skill.icon}</div>
              <div className="skill-title">{skill.title}</div>
              <div className="skill-tags">
                {skill.tags.map((tag) => (
                  <span key={tag} className="skill-tag">{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Projects ──────────────────────────────── */}
      <section style={{ padding: "80px 24px" }} id="projects">
        <div className="section-header">
          <div className="section-label">🔗 Projects & Experience</div>
          <h2 className="section-title">Real Work, Real Impact</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px", maxWidth: "1100px", margin: "0 auto" }}>
          {PROJECTS.map((project) => (
            <div
              key={project.name}
              className="skill-card"
              id={`project-${project.name.toLowerCase().replace(/\s+/g, "-")}`}
              style={{ background: "var(--bg-card)" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)" }}>
                    {project.name}
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                    {project.company}
                  </div>
                </div>
                <span style={{
                  padding: "4px 10px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: "700",
                  background: `${project.color}20`,
                  color: project.color,
                  border: `1px solid ${project.color}40`,
                  whiteSpace: "nowrap",
                }}>
                  {project.stat}
                </span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "14px" }}>
                {project.desc}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {project.tags.map((tag) => (
                  <span key={tag} className="skill-tag">{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Voice Agent ──────────────────────────── */}
      <section className="voice-section" id="voice">
        <div className="section-header">
          <div className="section-label">📞 Voice Agent</div>
          <h2 className="section-title">Call My AI Representative</h2>
        </div>

        <div className="voice-card">
          <div className="phone-icon-wrap">📞</div>
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>
            Call Devanshu&apos;s AI representative at:
          </p>
          <div className="phone-number" id="phone-number">
            +1 (540) 893 1058
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginBottom: "8px" }}>
            The agent will introduce itself, answer your questions about Devanshu&apos;s background,
            and can book a meeting on the spot.
          </p>
        </div>

      </section>

      {/* ── Booking ──────────────────────────────── */}
      <section id="book" className="booking-section">
        <div className="section-header">
          <div className="section-label">📅 Book a Meeting</div>
          <h2 className="section-title">Schedule Directly</h2>
          <p style={{ color: "var(--text-secondary)", marginTop: "12px", fontSize: "15px" }}>
            Real availability. Instant confirmation. No back-and-forth.
          </p>
        </div>
        <BookingSection calcomUsername={CALCOM_USERNAME} />
      </section>

      {/* ── Footer ──────────────────────────────── */}
      <footer style={{ padding: "32px 24px", borderTop: "1px solid var(--border)", textAlign: "center" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>
          Built by Devanshu Verma · IIIT Una · 2025 &nbsp;|&nbsp;{" "}
          <a
            href="https://github.com/devanshu119"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--accent-primary)", textDecoration: "none" }}
            id="footer-github-link"
          >
            github.com/devanshu119
          </a>
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "6px" }}>
          Powered by Vapi.ai · OpenAI · Pinecone · Cal.com · LangChain
        </p>
      </footer>
    </main>
  );
}
