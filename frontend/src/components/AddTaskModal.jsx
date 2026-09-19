import { S } from "../styles";
import { today, uid, addDays } from "../utils/dateHelpers";
import React, { useState, useEffect } from "react";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function AddTaskModalAarniHandoo24BCT0256({ taskToEdit, members, projectDeadline, onSave, onClose }) {
  const isEditing = !!taskToEdit;
  const memberNames = members.map(m => m.name).filter(Boolean);
  const [form, setForm] = useState({
    title: taskToEdit?.title || "",
    description: taskToEdit?.description || "",
    assignees: taskToEdit?.assignees || ["Team"],
    priority: taskToEdit?.priority || "MEDIUM",
    durationDays: taskToEdit?.durationDays || 3,
    startDate: taskToEdit?.startDate || today(),
    dueDate: taskToEdit?.dueDate || today(),
  });

  const toggleAssignee = name => setForm(prev => {
    const cur = prev.assignees || [];
    return { ...prev, assignees: cur.includes(name) ? cur.filter(n => n !== name) : [...cur, name] };
  });

  const handleSubmit = () => {
    if (!form.title || !form.dueDate) return;
    onSave(form);
  };

  return (
    <div style={S.overlay}>
      <div style={S.modal} className="modal-slide">
        <h3 style={S.modalTitle}>{isEditing ? "Edit Task" : "Add New Task"}</h3>
        <label style={S.label}>Task Title</label>
        <input style={S.input} value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className="pp-input" />
        <label style={S.label}>Description</label>
        <textarea style={S.textarea} rows={2} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} className="pp-input" />
        <label style={S.label}>Assignees</label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
          {["Team", ...memberNames].map(name => (
            <label key={name} style={S.checkboxLabel}>
              <input type="checkbox" checked={form.assignees.includes(name)} onChange={() => toggleAssignee(name)} />
              {name}
            </label>
          ))}
        </div>
        <div style={S.row2}>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Priority</label>
            <select style={S.input} value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} className="pp-input">
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Duration (days)</label>
            <input style={S.input} type="number" min="1" value={form.durationDays} onChange={e => setForm({ ...form, durationDays: parseInt(e.target.value) || 1 })} className="pp-input" />
          </div>
        </div>
        <div style={S.row2}>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Start Date</label>
            <input style={S.input} type="date" min={today()} value={form.startDate} onChange={e => setForm({ ...form, startDate: e.target.value })} className="pp-input" />
          </div>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Due Date</label>
            <input style={S.input} type="date" min={form.startDate || today()} max={projectDeadline || addDays(today(), 60)} value={form.dueDate} onChange={e => setForm({ ...form, dueDate: e.target.value })} className="pp-input" />
          </div>
        </div>
        <div style={S.modalBtns}>
          <button style={S.actionBtn("danger")} onClick={onClose} className="pp-task-btn">Cancel</button>
          <button style={S.actionBtn("success")} onClick={handleSubmit} className="pp-task-btn">{isEditing ? "Save Changes" : "Add Task"}</button>
        </div>
      </div>
    </div>
  );
}

export default AddTaskModalAarniHandoo24BCT0256;