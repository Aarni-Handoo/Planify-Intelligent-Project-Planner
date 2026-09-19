import { S } from "../styles";
import { today, diffDays, fmtDate } from "../utils/dateHelpers";
import { priorityColor, priorityBg } from "../utils/dateHelpers";
import React from "react";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function TaskCardAarniHandoo24BCT0256({ task, todayStr, onToggleComplete, onDelete, onShift, onEdit }) {
  const diff = diffDays(task.dueDate, todayStr);
  const isOverdue = !task.completed && diff < 0;
  const isDueToday = !task.completed && diff === 0;
  const isDueSoon = !task.completed && diff === 1;

  return (
    <div style={{ ...S.taskCard, borderLeft: `4px solid ${priorityColor(task.priority)}`, background: task.completed ? "#f8fafc" : priorityBg(task.priority), opacity: task.completed ? 0.65 : 1 }} className="task-card">
      <div style={S.taskTop}>
        <div style={S.taskLeft}>
          <span style={{ ...S.priorityBadge, background: `${priorityColor(task.priority)}18`, color: priorityColor(task.priority), border: `1px solid ${priorityColor(task.priority)}44` }}>{task.priority}</span>
          <span style={S.taskTitle}>{task.completed ? <s>{task.title}</s> : task.title}</span>
        </div>
        <div style={S.taskRight}>
          {isOverdue && <span style={S.badge("error")}>OVERDUE</span>}
          {isDueToday && <span style={S.badge("warn")}>DUE TODAY</span>}
          {isDueSoon && <span style={S.badge("info")}>TOMORROW</span>}
        </div>
      </div>
      <p style={S.taskDesc}>{task.description}</p>
      <div style={S.taskMeta}>
        <span style={S.metaChip}>👤 {task.assignees?.join(", ") || "Team"}</span>
        <span style={S.metaChip}>📅 {fmtDate(task.startDate)} → {fmtDate(task.dueDate)}</span>
        <span style={S.metaChip}>⏱ {task.durationDays}d</span>
      </div>
      <div style={S.taskActions}>
        <button style={S.actionBtn("success")} onClick={() => onToggleComplete(task.id)} className="pp-task-btn">
          {task.completed ? "↩ Undo" : "✓ Complete"}
        </button>
        {!task.completed && <>
          <button style={S.actionBtn("shift")} onClick={() => onShift(task.id)} className="pp-task-btn">📅 Shift</button>
          <button style={S.actionBtn("shift")} onClick={() => onEdit(task)} className="pp-task-btn">✏️ Edit</button>
        </>}
        <button style={S.actionBtn("danger")} onClick={() => onDelete(task.id)} className="pp-task-btn">🗑 Delete</button>
      </div>
    </div>
  );
}

export default TaskCardAarniHandoo24BCT0256;