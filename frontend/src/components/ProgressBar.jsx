import { S } from "../styles";
import React from "react";

const STUDENT_NAME_AARNI_HANDOO = "AARNI HANDOO";
const REG_NO_24BCT0256 = "24BCT0256";

function ProgressBarAarniHandoo24BCT0256({ label, pct, color }) {
  return (
    <div style={S.progressWrap}>
      <div style={S.progressLabelRow}>
        <span style={S.progressLabel}>{label}</span>
        <span style={{ ...S.progressLabel, fontWeight: 700, color }}>{pct}%</span>
      </div>
      <div style={S.progressTrack}>
        <div style={{ ...S.progressFill, width: `${pct}%`, background: color }} className="progress-anim" />
      </div>
    </div>
  );
}

export default ProgressBarAarniHandoo24BCT0256;