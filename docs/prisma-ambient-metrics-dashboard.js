/* Prisma Health ambient listening metrics — client-side engine (mirrors prisma_ambient_metrics.py) */

const HOSPITALS = [
  { key: "GREENVILLE MEMORIAL HOSPITAL", name: "Greenville Memorial Hospital", prefix: "GMH ", theme: "teal" },
  { key: "PATEWOOD MEMORIAL HOSPITAL", name: "Patewood Memorial Hospital", prefix: "PWH ", theme: "violet" },
  { key: "BAPTIST COLUMBIA HOSPITAL", name: "Baptist Columbia Hospital", prefix: "BCH ", theme: "amber" },
];

const CARE_PROVIDER_OPTIONS = [
  "Prisma",
  "HHC",
  "UMass",
  "Johns Hopkins",
  "Evergreen",
  "Kaiser",
  "University of Michigan",
  "Lee Health",
  "University of Oklahoma",
  "Intermountain",
  "Duke",
  "Norton",
  "St. Luke's",
  "Penn",
  "Baystate",
];

const BAPTIST_FACILITY = "BAPTIST COLUMBIA HOSPITAL";
const BAPTIST_CUTOFF = new Date("2026-07-01T00:00:00");
const DATE_START = new Date("2026-05-05T00:00:00");
const DATE_END = new Date("2026-07-21T23:59:59");
const ROUNDER_COLUMN = "Interaction Created By";
const UNIT_COLUMN = "Unit";

function norm(v) {
  return (v || "").trim().toLowerCase();
}

function parseCsvLine(line) {
  const out = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        cur += '"';
        i++;
      } else inQuotes = !inQuotes;
    } else if (ch === "," && !inQuotes) {
      out.push(cur);
      cur = "";
    } else cur += ch;
  }
  out.push(cur);
  return out;
}

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter((l) => l.trim());
  if (!lines.length) return { headers: [], rows: [] };
  const headers = parseCsvLine(lines[0]);
  const rows = lines.slice(1).map((line) => {
    const vals = parseCsvLine(line);
    const obj = {};
    headers.forEach((h, i) => {
      obj[h] = vals[i] ?? "";
    });
    return obj;
  });
  return { headers, rows };
}

function parseDate(value) {
  const v = (value || "").trim();
  if (!v) return null;
  const m = v.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4}) (\d{1,2}):(\d{2}) (AM|PM)/i);
  if (!m) return null;
  let hour = parseInt(m[4], 10);
  const min = parseInt(m[5], 10);
  if (m[6].toUpperCase() === "PM" && hour !== 12) hour += 12;
  if (m[6].toUpperCase() === "AM" && hour === 12) hour = 0;
  return new Date(parseInt(m[3], 10), parseInt(m[1], 10) - 1, parseInt(m[2], 10), hour, min);
}

function resolveDeclinedCol(headers) {
  const lower = Object.fromEntries(headers.map((h) => [h.trim().toLowerCase(), h]));
  for (const c of ["declined consent", "declined to record"]) {
    if (lower[c]) return lower[c];
  }
  throw new Error("CSV must include Declined Consent or Declined to Record");
}

function classifyRound(ambient, declined) {
  if (ambient === "yes" && declined === "no") return "al_used";
  if (ambient === "no" && declined === "yes") return "patient_said_no";
  if (ambient === "no" && declined === "no") return "manual_round";
  if (ambient === "yes" && declined === "yes") return "declined_during_al";
  return "other";
}

function pct(count, total) {
  return total ? Math.round((100 * count) / total * 10) / 10 : 0;
}

function formatDateRange(start, end) {
  const mo = (d) => d.toLocaleString("en-US", { month: "long" });
  if (start.getFullYear() === end.getFullYear()) {
    return `${mo(start)} ${start.getDate()} – ${mo(end)} ${end.getDate()}, ${end.getFullYear()}`;
  }
  return `${mo(start)} ${start.getDate()}, ${start.getFullYear()} – ${mo(end)} ${end.getDate()}, ${end.getFullYear()}`;
}

function summarizeRows(rows) {
  const counts = { al_used: 0, patient_said_no: 0, manual_round: 0, declined_during_al: 0 };
  const unitStats = new Map();

  for (const row of rows) {
    const outcome = classifyRound(row.ambient, row.declined);
    if (counts[outcome] !== undefined) counts[outcome]++;
    if (!unitStats.has(row.unit)) {
      unitStats.set(row.unit, { total: 0, al_used: 0, patient_said_no: 0, manual_round: 0, declined_during_al: 0 });
    }
    const u = unitStats.get(row.unit);
    u.total++;
    if (u[outcome] !== undefined) u[outcome]++;
  }

  const total = rows.length;
  const units = [...unitStats.entries()]
    .sort((a, b) => b[1].total - a[1].total || a[0].localeCompare(b[0]))
    .map(([unit, s]) => {
      const declinedOrNo = s.patient_said_no + s.declined_during_al;
      return {
        unit,
        ...s,
        declined_or_no: declinedOrNo,
        al_used_pct: pct(s.al_used, s.total),
        patient_said_no_pct: pct(s.patient_said_no, s.total),
        manual_round_pct: pct(s.manual_round, s.total),
        declined_during_al_pct: pct(s.declined_during_al, s.total),
        declined_or_no_pct: pct(declinedOrNo, s.total),
      };
    });

  const declinedOrNo = counts.patient_said_no + counts.declined_during_al;
  return {
    total_rounds: total,
    al_used: counts.al_used,
    al_used_pct: pct(counts.al_used, total),
    patient_said_no: counts.patient_said_no,
    patient_said_no_pct: pct(counts.patient_said_no, total),
    manual_round: counts.manual_round,
    manual_round_pct: pct(counts.manual_round, total),
    declined_during_al: counts.declined_during_al,
    declined_during_al_pct: pct(counts.declined_during_al, total),
    declined_or_no: declinedOrNo,
    declined_or_no_pct: pct(declinedOrNo, total),
    al_attempted: counts.al_used + counts.declined_during_al,
    units,
  };
}

function parseAllRows(csvText) {
  const { headers, rows: rawRows } = parseCsv(csvText);
  const declinedCol = resolveDeclinedCol(headers);
  const hospitalKeys = new Set(HOSPITALS.map((h) => h.key));
  const parsedRows = [];

  for (const row of rawRows) {
    const facility = (row["Unit Facility"] || "").trim().toUpperCase();
    if (!hospitalKeys.has(facility)) continue;
    const dt = parseDate(row["Interaction Time"]);
    if (!dt || dt < DATE_START || dt > DATE_END) continue;
    parsedRows.push({
      facility,
      ambient: norm(row["Ambient Listening"]),
      declined: norm(row[declinedCol]),
      unit: (row[UNIT_COLUMN] || "Unknown").trim(),
      rounder: (row[ROUNDER_COLUMN] || "Unknown").trim(),
      interaction_time: dt,
    });
  }
  return parsedRows;
}

function listFilterOptions(csvText) {
  const rows = parseAllRows(csvText);
  return {
    rounders: [...new Set(rows.map((r) => r.rounder))].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" })),
    units: [...new Set(rows.map((r) => r.unit))].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" })),
  };
}

function computeMetrics(csvText, filters = {}) {
  const careProvider = (filters.careProvider || "").trim();
  const rounder = (filters.rounder || "").trim();
  const unit = (filters.unit || "").trim();
  let parsedRows = parseAllRows(csvText);
  const filterOptions = listFilterOptions(csvText);

  if (rounder) parsedRows = parsedRows.filter((r) => r.rounder === rounder);
  if (unit) parsedRows = parsedRows.filter((r) => r.unit === unit);

  const dates = parsedRows.map((r) => r.interaction_time);
  const dateStart = dates.length ? new Date(Math.min(...dates)) : DATE_START;
  const dateEnd = dates.length ? new Date(Math.max(...dates)) : DATE_END;

  const results = { _report: {} };
  for (const h of HOSPITALS) {
    results[h.name] = summarizeRows(parsedRows.filter((r) => r.facility === h.key));
  }

  const baptistRows = parsedRows.filter((r) => r.facility === BAPTIST_FACILITY);
  const before = baptistRows.filter((r) => r.interaction_time < BAPTIST_CUTOFF);
  const after = baptistRows.filter((r) => r.interaction_time >= BAPTIST_CUTOFF);

  results._report = {
    date_range_label: formatDateRange(dateStart, dateEnd),
    care_provider: careProvider,
    rounder,
    unit,
    filter_options: filterOptions,
    row_count: parsedRows.length,
    baptist_before_after: {
      before_label: "Before July 1",
      after_label: "July 1 Onward",
      before_period: formatDateRange(dateStart, new Date("2026-06-30T23:59:59")),
      after_period: formatDateRange(BAPTIST_CUTOFF, dateEnd),
      before: summarizeRows(before),
      after: summarizeRows(after),
    },
  };

  return results;
}

function formatFilterStatus(filters = {}) {
  const parts = [];
  const careProvider = (filters.careProvider || "").trim();
  const rounder = (filters.rounder || "").trim();
  const unit = (filters.unit || "").trim();
  if (careProvider) parts.push(careProvider);
  if (rounder) parts.push(rounder);
  if (unit) parts.push(unit);
  return parts.join(" · ");
}

function slideHeaderCustomer(careProvider) {
  if (!careProvider) return "";
  return `<div class="header-meta"><p class="customer">${careProvider}</p><p class="doc-type">CipherRounds · Ambient Listening · 2026</p></div>`;
}

function titleWithProvider(baseTitle, providerLabel) {
  if (!providerLabel) return baseTitle;
  return `${baseTitle} · ${providerLabel}`;
}

function renderHospitalCard(hospital, metrics, providerLabel) {
  const m = metrics[hospital.name];
  const unitRows = m.units
    .slice(0, 12)
    .map(
      (u) =>
        `<tr><td>${u.unit.replace(hospital.prefix, "")}</td><td>${fmt(u.total)}</td><td>${u.al_used}</td><td>${u.patient_said_no}</td><td>${fmt(u.manual_round)}</td><td>${u.declined_during_al}</td><td>${u.declined_or_no_pct}%</td></tr>`
    )
    .join("");
  const extra = m.units.length > 12 ? `<p class="table-note">+ ${m.units.length - 12} more units</p>` : "";

  return `
    <article class="slide hospital-slide hospital-${hospital.theme}">
      <header class="slide-header">
        <div class="brand">CipherHealth</div>
        ${slideHeaderCustomer(providerLabel)}
      </header>
      <div class="title-band"><h2>${titleWithProvider("Unit Breakdown", providerLabel)}</h2><p class="subtitle">${metrics._report.date_range_label}</p></div>
      <div class="hospital-body">
        <div class="metric-pills">
          <div class="pill"><span>AL Used</span><strong>${m.al_used_pct}%</strong></div>
          <div class="pill"><span>Patient Said No</span><strong>${m.patient_said_no_pct}%</strong></div>
          <div class="pill"><span>Manual Round</span><strong>${m.manual_round_pct}%</strong></div>
        </div>
        <table class="unit-table"><thead><tr><th>Unit</th><th>Total</th><th>AL Used</th><th>Pt Said No</th><th>Manual</th><th>Decl During AL</th><th>% Pt/Staff No</th></tr></thead><tbody>${unitRows}</tbody></table>
        ${extra}
      </div>
      <footer class="slide-footer"><span>Confidential · cipherhealth.com</span></footer>
    </article>`;
}

function renderSummarySlide(metrics, providerLabel) {
  const cards = HOSPITALS.map((h) => {
    const m = metrics[h.name];
    return `
      <section class="hospital-card hospital-${h.theme}">
        <h3>${h.name.replace(" Hospital", "")}</h3>
        <p class="total">${fmt(m.total_rounds)} rounds</p>
        <div class="metric-pills compact">
          <div class="pill"><span>AL Used</span><strong>${m.al_used_pct}%</strong></div>
          <div class="pill"><span>Patient Said No</span><strong>${m.patient_said_no_pct}%</strong></div>
          <div class="pill"><span>Manual</span><strong>${m.manual_round_pct}%</strong></div>
        </div>
        <ul class="counts">
          <li>AL used: ${fmt(m.al_used)}</li>
          <li>Declined during AL: ${fmt(m.declined_during_al)} (${m.declined_during_al_pct}%)</li>
          <li>Patient/staff no: ${m.declined_or_no_pct}%</li>
        </ul>
      </section>`;
  }).join("");

  const r = metrics._report;
  const baptist = r.baptist_before_after;
  const insight = `Baptist after July 1: ${fmt(baptist.after.total_rounds)} rounds, AL used ${baptist.after.al_used_pct}% — see slide 5.`;

  return `
    <article class="slide summary-slide">
      <header class="slide-header">
        <div class="brand">CipherHealth</div>
        ${slideHeaderCustomer(providerLabel)}
      </header>
      <div class="title-band">
        <h2>Ambient Listening Adoption Metrics</h2>
        <p class="subtitle">${r.date_range_label}${providerLabel ? ` · ${providerLabel}` : ""}</p>
      </div>
      <div class="summary-grid">${cards}</div>
      <div class="insights"><strong>Key insight</strong><p>${insight}</p></div>
      <footer class="slide-footer"><span>Source: interaction export · ${fmt(r.row_count)} rows in view</span></footer>
    </article>`;
}

function renderBaptistAfterSlide(metrics, providerLabel) {
  const c = metrics._report.baptist_before_after;
  const after = c.after;
  const baptist = HOSPITALS.find((h) => h.key === "BAPTIST COLUMBIA HOSPITAL");
  const unitRows = after.units
    .slice(0, 12)
    .map(
      (u) =>
        `<tr><td>${u.unit.replace(baptist.prefix, "")}</td><td>${fmt(u.total)}</td><td>${u.al_used}</td><td>${u.patient_said_no}</td><td>${fmt(u.manual_round)}</td><td>${u.declined_during_al}</td><td>${u.declined_or_no_pct}%</td></tr>`
    )
    .join("");
  const extra = after.units.length > 12 ? `<p class="table-note">+ ${after.units.length - 12} more units</p>` : "";

  return `
    <article class="slide compare-slide">
      <header class="slide-header">
        <div class="brand">CipherHealth</div>
        ${slideHeaderCustomer(providerLabel)}
      </header>
      <div class="title-band">
        <h2>${titleWithProvider("Baptist Columbia · After July 1", providerLabel)}</h2>
        <p class="subtitle">${c.after_period} · ${fmt(after.total_rounds)} rounds · AL used ${after.al_used_pct}%</p>
      </div>
      <div class="hospital-body">
        <div class="metric-pills">
          <div class="pill"><span>AL Used</span><strong>${after.al_used_pct}%</strong></div>
          <div class="pill"><span>Patient Said No</span><strong>${after.patient_said_no_pct}%</strong></div>
          <div class="pill"><span>Manual Round</span><strong>${after.manual_round_pct}%</strong></div>
        </div>
        <table class="unit-table"><thead><tr><th>Unit</th><th>Total</th><th>AL Used</th><th>Pt Said No</th><th>Manual</th><th>Decl During AL</th><th>% Pt/Staff No</th></tr></thead><tbody>${unitRows}</tbody></table>
        ${extra}
      </div>
      <footer class="slide-footer"><span>July 1 – July 22 · Baptist Columbia Hospital only</span></footer>
    </article>`;
}

function renderDashboard(metrics, providerLabel) {
  const label = providerLabel || "";
  return [
    renderSummarySlide(metrics, label),
    ...HOSPITALS.map((h) => renderHospitalCard(h, metrics, label)),
    renderBaptistAfterSlide(metrics, label),
  ].join("");
}

window.PrismaAmbientMetrics = {
  HOSPITALS,
  CARE_PROVIDER_OPTIONS,
  computeMetrics,
  listFilterOptions,
  renderDashboard,
  formatProviderLabel: (careProvider) => (careProvider || "").trim(),
  formatFilterStatus,
  fmt,
};
