import { S } from "../styles";
import React, { useState, useEffect } from "react";
import { today, fmtDate } from "../utils/dateHelpers";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function ShiftModalAarniHandoo24BCT0256({ task, onConfirm, onClose }) {
  const [date, setDate] = useState(task?.dueDate || today());
  return (
    <div style={S.overlay}>
      <div style={S.modal} className="modal-slide">
        <h3 style={S.modalTitle}>Shift Deadline</h3>
        <p style={{ color: "#64748b", fontSize: 14, marginBottom: 16 }}>
          <strong>{task?.title}</strong><br />
          Current: {fmtDate(task?.dueDate)}
        </p>
        <label style={S.label}>New Deadline</label>
        <input style={S.input} type="date" min={today()} value={date} onChange={e => setDate(e.target.value)} className="pp-input" />
        <div style={S.modalBtns}>
          <button style={S.actionBtn("shift")} onClick={() => onConfirm(date)} className="pp-task-btn">Confirm Shift</button>
          <button style={S.actionBtn("danger")} onClick={onClose} className="pp-task-btn">Cancel</button>
        </div>
      </div>
    </div>
  );
}

export default ShiftModalAarniHandoo24BCT0256;