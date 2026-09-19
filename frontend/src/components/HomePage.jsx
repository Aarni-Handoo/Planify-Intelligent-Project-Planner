import React, { useState } from "react";
import { HS } from "../styles";
import { priorityColor } from "../utils/dateHelpers";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

const HomePageAarniHandoo24BCT0256 = ({ onNewProject, onJoinProject, loading, loadMsg }) => {
  const [joinCode, setJoinCode] = useState("");
  const [joinError, setJoinError] = useState("");
  const [joinFocused, setJoinFocused] = useState(false);

  const features = [
    { icon: "🎯", title: "Smart Task Planning",    desc: "AI-powered task suggestions in a logical sequence from kickoff to handover." },
    { icon: "👥", title: "Role-Based Assignment",  desc: "Auto-assigns tasks based on member skills — frontend, backend, design & more." },
    { icon: "📊", title: "Live Progress Tracking", desc: "Visual dashboards, overdue alerts, and deadline meeting rate at a glance." },
    { icon: "📅", title: "Flexible Scheduling",    desc: "Shift deadlines, edit tasks, and cascade changes to dependent work instantly." },
  ];

  const steps = [
    { n: "01", label: "Name Your Project", desc: "Set a name, start date, and deadline." },
    { n: "02", label: "Add Team Members",  desc: "List each person and their skills." },
    { n: "03", label: "Generate Tasks",    desc: "Get a smart, sequenced task plan instantly." },
    { n: "04", label: "Share & Collaborate", desc: "Share your unique code so teammates can join." },
  ];

  const handleJoinAarniHandoo24BCT0256 = () => {
    const trimmed = joinCode.trim();
    if (!trimmed) { setJoinError("Please enter a project code."); return; }
    if (trimmed.length < 5)  { setJoinError("Codes are at least 5 characters."); return; }
    setJoinError("");
    onJoinProject(trimmed);
  };

  const handleKeyDownAarniHandoo24BCT0256 = (e) => {
    if (e.key === "Enter") handleJoinAarniHandoo24BCT0256();
  };

  return (
    <div style={HS.page}>
      <nav style={HS.nav}>
        <div style={HS.logo}>
          <span style={HS.logoMark}>◈</span>
          <span style={HS.logoName}>Planify</span>
        </div>
        <div style={HS.navLinks}>
          <a href="#features" style={HS.navLink}> Features</a>
          <a href="#how"      style={HS.navLink}>How it works</a>
          <a 
            href="/resume.html"
            target="_blank"
            rel="noopener noreferrer"
            style={HS.navLink}
          >
          My Portfolio
          </a>
        </div>
        <button onClick={onNewProject} style={HS.navCta} className="hp-btn">
          Plan a Project →
        </button>
      </nav>

      <section style={HS.hero}>
        <div style={HS.heroTag} className="fade-up">Track Your Progress · Avoid Delays</div>

        <h1 style={HS.heroTitle} className="fade-up delay-1">
          Plan smarter.<br />
          <span style={HS.heroAccent}>Innovate faster.</span>
        </h1>

        <p style={HS.heroSub} className="fade-up delay-2">
          From kickoff to handover — auto-generate task sequences assigned by skill,
          track your team's progress with beautiful dashboards, and collaborate via a shared project code.
        </p>

        <div style={HS.heroActions} className="fade-up delay-3">
          <div style={HS.actionCard} className="action-card">
            <div style={HS.actionCardIcon}>🚀</div>
            <div style={HS.actionCardBody}>
              <div style={HS.actionCardTitle}>Plan a New Project</div>
              <div style={HS.actionCardDesc}>Start fresh — get a unique code to share with your team.</div>
            </div>
            <button
              onClick={onNewProject}
              style={HS.actionCardBtn}
              className="hp-cta-btn"
              disabled={loading}
            >
              {loading && loadMsg ? <span style={{ fontSize: 13 }}>⏳ {loadMsg}</span> : <>Start <span style={HS.ctaArrow}>→</span></>}
            </button>
          </div>

          <div style={HS.orDivider}>
            <div style={HS.orLine} />
            <span style={HS.orText}>or</span>
            <div style={HS.orLine} />
          </div>

          <div style={{ ...HS.actionCard, ...(joinFocused ? HS.actionCardFocused : {}) }} className="action-card">
            <div style={HS.actionCardIcon}>🔗</div>
            <div style={HS.actionCardBody}>
              <div style={HS.actionCardTitle}>Join a Project</div>
              <div style={HS.actionCardDesc}>Enter your team's project code to join their workspace.</div>
              <div style={HS.joinInputRow}>
                <input
                  style={{
                    ...HS.joinInput,
                    borderColor: joinError ? "#ef4444" : joinFocused ? "#4f46e5" : "#e2e8f0",
                    boxShadow: joinFocused ? "0 0 0 3px rgba(79,70,229,.12)" : "none",
                  }}
                  placeholder="e.g.  K7X-4M2"
                  value={joinCode}
                  onChange={e => { setJoinCode(e.target.value.toUpperCase()); setJoinError(""); }}
                  onKeyDown={handleKeyDownAarniHandoo24BCT0256}
                  onFocus={() => setJoinFocused(true)}
                  onBlur={() => setJoinFocused(false)}
                  maxLength={10}
                  spellCheck={false}
                />
                <button
                  style={HS.joinBtn}
                  onClick={handleJoinAarniHandoo24BCT0256}
                  disabled={loading}
                  className="hp-join-btn"
                >
                  {loading && loadMsg ? "…" : "Join"}
                </button>
              </div>
              {joinError && <div style={HS.joinError}>{joinError}</div>}
            </div>
          </div>
        </div>

        <div style={HS.heroCard} className="fade-up delay-4">
          <div style={HS.heroCardInner}>
            <div style={HS.heroCardHeader}>
              <div style={dot("#10b981")} /><div style={dot("#f59e0b")} /><div style={dot("#ef4444")} />
              <span style={HS.heroCardTitle}>Medicine Scanner WebApp &nbsp;·&nbsp; 18 days left</span>
              <span style={HS.heroCodePill}>K7X-4M2</span>
            </div>
            <div style={HS.heroProgressRow}>
              <span style={HS.heroProgressLabel}>Overall Completion</span>
              <span style={HS.heroProgressPct}>64%</span>
            </div>
            <div style={HS.heroProgressTrack}>
              <div style={{ ...HS.heroProgressFill, width: "64%" }} className="progress-anim" />
            </div>
            <div style={HS.heroTaskList}>
              {[
                { t: "UI/UX Wireframing",    done: true,  p: "HIGH"   },
                { t: "Backend API Setup",    done: true,  p: "HIGH"   },
                { t: "Frontend Integration", done: false, p: "HIGH"   },
                { t: "Testing & QA",         done: false, p: "MEDIUM" },
              ].map((item, i) => (
                <div key={i} style={HS.heroTaskItem}>
                  <span style={{ ...HS.heroTaskDot, background: item.done ? "#10b981" : "#e2e8f0" }} />
                  <span style={{ ...HS.heroTaskLabel, textDecoration: item.done ? "line-through" : "none", color: item.done ? "#94a3b8" : "#1e293b" }}>
                    {item.t}
                  </span>
                  <span style={{ ...HS.heroTaskBadge, color: priorityColor(item.p) }}>{item.p}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="features" style={HS.section}>
        <div style={HS.sectionTag}>Features</div>
        <h2 style={HS.sectionTitle}>Everything your team needs</h2>
        <div style={HS.featureGrid}>
          {features.map((f, i) => (
            <div key={i} style={HS.featureCard} className="feature-card">
              <div style={HS.featureIcon}>{f.icon}</div>
              <h3 style={HS.featureTitle}>{f.title}</h3>
              <p style={HS.featureDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how" style={{ ...HS.section, maxWidth: "1100px", margin: "60px auto 100px", background: "rgba(99,102,241,.04)", borderRadius: 24, width: "100%" }}>
        <div style={HS.sectionTag}>Process</div>
        <h2 style={HS.sectionTitle}>How it works</h2>
        <div style={HS.stepsRow}>
          {steps.map((s, i) => (
            <div key={i} style={HS.step} className="step-card">
              <div style={HS.stepNum}>{s.n}</div>
              <h4 style={HS.stepLabel}>{s.label}</h4>
              <p style={HS.stepDesc}>{s.desc}</p>
              {i < steps.length - 1 && <div style={HS.stepArrow}>→</div>}
            </div>
          ))}
        </div>
      </section>

      <footer style={HS.footer}>
        <span style={HS.logo}>
          <span style={HS.logoMark}>◈</span>
          <span style={HS.logoName}>Planify</span>
        </span>
        <span style={{ color: "#94a3b8", fontSize: 13 }}>© 2026 {STUDENT_NAME_AARNI_HANDOO} ({REG_NO_24BCT0256}). All rights reserved.</span>
      </footer>
    </div>
  );
};

const dot = (c) => ({ width: 10, height: 10, borderRadius: "50%", background: c, flexShrink: 0 });

export default HomePageAarniHandoo24BCT0256;