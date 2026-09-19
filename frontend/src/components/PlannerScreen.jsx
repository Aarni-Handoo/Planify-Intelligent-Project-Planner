import React, { useState, useEffect } from "react";
import TaskCardAarniHandoo24BCT0256 from "./TaskCard";
import ProgressBarAarniHandoo24BCT0256 from "./ProgressBar";
import { S } from "../styles";
import { today, diffDays, fmtDate, priorityColor } from "../utils/dateHelpers";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function PlannerScreenAarniHandoo24BCT0256({
  project, tasks, members, pct, deadlinePct,
  projectCode,
  onToggleComplete, onDelete, onShift, onAddTask, onEditTask,
  onRecommend, onReset, onDeleteProject,
  onUpdateNotes,
  loading
}) {
  const [filter, setFilter] = useState("ALL");
  const [sortMode, setSortMode] = useState("start");
  const [codeCopied, setCodeCopied] = useState(false);
  const todayStr = today();

  const copyCode = () => {
    navigator.clipboard.writeText(projectCode).then(() => {
      setCodeCopied(true);
      setTimeout(() => setCodeCopied(false), 2000);
    });
  };

  const sorted = [...tasks].sort((a, b) => {
    if (sortMode === "start") return new Date(a.startDate) - new Date(b.startDate);
    if (sortMode === "due") return new Date(a.dueDate) - new Date(b.dueDate);
    if (sortMode === "duration") return b.durationDays - a.durationDays;
    return 0;
  });

  const filtered = sorted.filter(t => {
    if (filter === "ALL") return true;
    if (filter === "HIGH") return t.priority === "HIGH";
    if (filter === "MEDIUM") return t.priority === "MEDIUM";
    if (filter === "LOW") return t.priority === "LOW";
    if (filter === "PENDING") return !t.completed;
    if (filter === "DONE") return t.completed;
    return true;
  });

  const upcoming = sorted.filter(t => !t.completed).slice(0, 3);
  const overdue = tasks.filter(t => !t.completed && t.dueDate < todayStr).length;

  return (
    <div style={S.plannerWrap}>
      <div style={S.plannerHeader}>
        <div>
          <div style={S.logoRow}>
            <span style={S.logoMark}>◈</span>
            <span style={S.logoName}>Planify</span>
          </div>
          <h2 style={S.projectTitle}>{project.name}</h2>
          <p style={S.projectDeadline}>
            {fmtDate(project.startDate)} → <strong>{fmtDate(project.deadline)}</strong>
          </p>
        </div>

        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 10 }}>
          {projectCode && (
            <div style={S.codeBadge} onClick={copyCode} title="Click to copy" className="code-badge">
              <span style={S.codeIcon}>🔗</span>
              <span style={S.codeText}>{projectCode}</span>
              <span style={S.codeCopyHint}>{codeCopied ? "✓ Copied!" : "Copy"}</span>
            </div>
          )}

          <div style={{ display: "flex", gap: 8 }}>
            <button style={S.resetBtn} onClick={onReset} className="pp-ghost-btn">
              ← New Project
            </button>
            <button
              onClick={onDeleteProject}
              style={{
                background: "#ef4444",
                color: "#fff",
                border: "none",
                borderRadius: 10,
                padding: "9px 18px",
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 1px 4px rgba(0,0,0,.1)"
              }}
              className="pp-ghost-btn"
            >
              🗑️ Delete Project
            </button>
          </div>
        </div>
      </div>

      <div style={S.statsRow}>
        {[
          { icon: "📋", label: "Total Tasks", value: tasks.length },
          { icon: "✅", label: "Completed", value: tasks.filter(t => t.completed).length },
          { icon: "🔴", label: "High Priority", value: tasks.filter(t => t.priority === "HIGH" && !t.completed).length },
          { icon: "⏰", label: "Overdue", value: overdue },
        ].map((s, i) => (
          <div
            key={i}
            style={{ ...S.statCard, borderTop: `3px solid ${i === 3 && overdue > 0 ? "#ef4444" : "#6366f1"}` }}
            className="stat-card"
          >
            <div style={S.statIcon}>{s.icon}</div>
            <div style={{ ...S.statValue, color: i === 3 && overdue > 0 ? "#ef4444" : "#1e293b" }}>{s.value}</div>
            <div style={S.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={S.progressSection}>
        <ProgressBarAarniHandoo24BCT0256 label="Overall Completion" pct={pct} color="#6366f1" />
        <ProgressBarAarniHandoo24BCT0256
          label="On-Time Completion Rate"
          pct={deadlinePct}
          color={deadlinePct >= 80 ? "#10b981" : deadlinePct >= 50 ? "#f9c873" : "#ef4444"}
        />
      </div>

      <div style={S.notesBox}>
        <div style={S.boxTitle}>📝 Project Notes / Reviews</div>
        <textarea
          style={S.textarea}
          rows={3}
          placeholder="Add notes, review links, client feedback…"
          value={project.notes || ""}
          onChange={e => onUpdateNotes(e.target.value)}
          className="pp-input"
        />
      </div>

      {upcoming.length > 0 && (
        <div style={S.remindersBox}>
          <div style={S.boxTitle}>⏰ Upcoming Deadlines</div>
          {upcoming.map(t => {
            const diff = diffDays(t.dueDate, todayStr);
            return (
              <div key={t.id} style={{ ...S.reminderChip, borderLeft: `3px solid ${priorityColor(t.priority)}` }}>
                <strong style={{ color: "#1e293b" }}>{t.title}</strong>
                <span style={{ color: "#64748b", fontSize: 12 }}>
                  {diff <= 0 ? " — TODAY / OVERDUE" : diff === 1 ? " — Tomorrow" : ` — in ${diff}d`}
                </span>
                <span style={S.assigneeTag}>{t.assignees?.join(", ") || "Team"}</span>
              </div>
            );
          })}
        </div>
      )}

      <div style={S.controlsRow}>
        <div style={S.sortGroup}>
          {[["start", "📅 Start Date"], ["due", "📅 Due Date"], ["duration", "⏱ Duration"]].map(([m, label]) => (
            <button
              key={m}
              style={{ ...S.filterBtn, ...(sortMode === m ? S.filterActive : {}) }}
              onClick={() => setSortMode(m)}
              className="pp-filter-btn"
            >
              {label}
            </button>
          ))}
        </div>
        <div style={S.actionGroup}>
          <button style={S.addTaskBtn} onClick={onAddTask} className="pp-action-btn">+ Add Task</button>
          <button style={S.suggestBtn} onClick={onRecommend} disabled={loading} className="pp-suggest-btn">
            {loading ? "⏳ Generating…" : "✦ Suggest Tasks"}
          </button>
        </div>
      </div>

      <div style={S.filterBar}>
        {["ALL", "HIGH", "MEDIUM", "LOW", "PENDING", "DONE"].map(f => (
          <button
            key={f}
            style={{ ...S.filterBtn, ...(filter === f ? S.filterActive : {}) }}
            onClick={() => setFilter(f)}
            className="pp-filter-btn"
          >
            {f === "HIGH" && <span style={{ color: "#ef4444" }}>● </span>}
            {f === "MEDIUM" && <span style={{ color: "#f9c873" }}>● </span>}
            {f === "LOW" && <span style={{ color: "#10b981" }}>● </span>}
            {f}
          </button>
        ))}
      </div>

      <div style={S.taskList}>
        {filtered.map(t => (
          <TaskCardAarniHandoo24BCT0256
            key={t.id} task={t} todayStr={todayStr}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            onShift={onShift}
            onEdit={onEditTask}
          />
        ))}
        {filtered.length === 0 && (
          <div style={S.emptyState}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
            No tasks yet.<br />
            <span style={{ fontSize: 14, color: "#94a3b8" }}>
              Click <strong>"✦ Suggest Tasks"</strong> for a smart plan, or add manually.
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default PlannerScreenAarniHandoo24BCT0256;