import { S } from "../styles";
import { today, uid } from "../utils/dateHelpers";
import React from "react";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function SpinnerAarniHandoo24BCT0256() {
  return <span className="spin">⟳</span>;
}

const SetupScreenAarniHandoo24BCT0256 = ({ project, setProject, members, setMembers, onStart, onBack, loading, loadMsg }) => {
  const addMemberAarniHandoo24BCT0256 = () => setMembers(p => [...p, { id: uid(), name: "", skills: "" }]);
  const removeMemberAarniHandoo24BCT0256 = id => setMembers(p => p.filter(m => m.id !== id));
  const updateMemberAarniHandoo24BCT0256 = (id, field, val) => setMembers(p => p.map(m => m.id === id ? { ...m, [field]: val } : m));

 return (
    <div style={S.setupWrap}>
      <div style={S.setupCard} className="fade-up">
        <button onClick={onBack} style={S.backBtn}>← Back</button>
        <div style={S.logoRow}>
          <span style={S.logoMark}>◈</span>
          <span style={S.logoName}>Planify</span>
        </div>
        <h1 style={S.setupTitle}>New Project</h1>
        <p style={S.setupSub}>Fill in the details and we'll build your smart task plan.</p>

        <div style={S.section}>
          <label style={S.label}>Project Name</label>
          <input style={S.input} placeholder="e.g. Aarni's Web App" value={project.name} onChange={e => setProject({ ...project, name: e.target.value })} className="pp-input" />
        </div>

        <div style={S.row2}>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Start Date</label>
            <input style={S.input} type="date" min={today()} value={project.startDate} onChange={e => setProject({ ...project, startDate: e.target.value })} className="pp-input" />
          </div>
          <div style={{ flex: 1 }}>
            <label style={S.label}>Deadline</label>
            <input style={S.input} type="date" min={project.startDate || today()} value={project.deadline} onChange={e => setProject({ ...project, deadline: e.target.value })} className="pp-input" />
          </div>
        </div>

        <div style={S.section}>
          <label style={S.label}>Description <span style={S.optional}>(optional)</span></label>
          <textarea style={S.textarea} rows={3} placeholder="Brief overview of goals and scope…" value={project.description} onChange={e => setProject({ ...project, description: e.target.value })} className="pp-input" />
        </div>

        <div style={S.section}>
          <label style={S.label}>Notes / Reviews <span style={S.optional}>(optional)</span></label>
          <textarea style={S.textarea} rows={2} placeholder="Any comments, client notes, review links..." value={project.notes} onChange={e => setProject({ ...project, notes: e.target.value })} className="pp-input" />
        </div>

        <div style={S.section}>
          <div style={S.memberHeader}>
            <label style={S.label}>Team Members</label>
            <button style={S.addBtn} onClick={addMemberAarniHandoo24BCT0256} className="pp-add-btn">+ Add Member</button>
          </div>
          <div style={S.skillHint}>💡 Skills like <em>React, Figma, Node, Backend</em> help auto-assign tasks correctly.</div>
          {members.map((m, i) => (
            <div key={m.id} style={S.memberRow}>
              <span style={S.memberIdx}>{i + 1}</span>
              <input style={{ ...S.input, flex: 1 }} placeholder="Name" value={m.name} onChange={e => updateMemberAarniHandoo24BCT0256(m.id, "name", e.target.value)} className="pp-input" />
              <input style={{ ...S.input, flex: 2 }} placeholder="Skills (React, Figma, Node, Backend…)" value={m.skills} onChange={e => updateMemberAarniHandoo24BCT0256(m.id, "skills", e.target.value)} className="pp-input" />
              {members.length > 1 && <button style={S.removeBtn} onClick={() => removeMemberAarniHandoo24BCT0256(m.id)} className="pp-remove-btn">✕</button>}
            </div>
          ))}
        </div>

        <button style={S.generateBtn} onClick={onStart} disabled={loading} className="pp-launch-btn">
          {loading ? <span style={S.loadRow}><SpinnerAarniHandoo24BCT0256 /> {loadMsg}</span> : "Launch Planner 🧠"}
        </button>
      </div>
    </div>
  );
};

export default SetupScreenAarniHandoo24BCT0256;