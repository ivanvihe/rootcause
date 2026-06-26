const summaryCards = document.querySelector("#summary-cards");
const alertList = document.querySelector("#alert-list");
// Unified search: the header search box also live-filters the sidebar alert list.
const alertSearch = document.querySelector("#global-search-input");
const newAlertButton = document.querySelector("#new-alert-button");
const alertTemplate = document.querySelector("#alert-item-template");
const sidebarOverview = document.querySelector("#sidebar-overview");
const homeButton = document.querySelector("#home-button");
const globalSearchForm = document.querySelector("#global-search-form");
const globalSearchInput = document.querySelector("#global-search-input");
const notificationsButton = document.querySelector("#notifications-button");
const notificationsPopup = document.querySelector("#notifications-popup");
const workspaceTitle = document.querySelector("#workspace-title");
const executionsTable = document.querySelector("#executions-table");
const executionsTitle = document.querySelector("#executions-title");
const executionCount = document.querySelector("#execution-count");
const hostsCount = document.querySelector("#hosts-count");
const hostsEditTable = document.querySelector("#hosts-edit-table");
const hostsPreview = document.querySelector("#hosts-preview");
const hostsPreviewCount = document.querySelector("#hosts-preview-count");
const jsonPreview = document.querySelector("#json-preview");
const scheduleInput = document.querySelector("#edit-schedule");
const deleteAlertButton = document.querySelector("#delete-alert-button");
const rearmAlertButton = document.querySelector("#rearm-alert-button");
const saveStatus = document.querySelector("#save-status");
const newHostButton = document.querySelector("#new-host-button");
const headerStatus = document.querySelector("#header-status");
const homeView = document.querySelector("#home-view");
const problemsView = document.querySelector("#problems-view");
const problemsTable = document.querySelector("#problems-table");
const problemsCount = document.querySelector("#problems-count");
const searchView = document.querySelector("#search-view");
const alertView = document.querySelector("#alert-view");
const alertSideColumn = document.querySelector("#alert-side-column");
const dashboardCards = document.querySelector("#dashboard-cards");
const dashboardGrafanaFrame = document.querySelector("#dashboard-grafana-frame");
const dashboardOpenGrafana = document.querySelector("#dashboard-open-grafana");
const dashboardStatusBanner = document.querySelector("#status-banner");
const dashboardAlertsTable = document.querySelector("#dashboard-alerts-table");
const externalAlertsCount = document.querySelector("#external-alerts-count");
const externalAlertsTable = document.querySelector("#external-alerts-table");
const searchResultsTitle = document.querySelector("#search-results-title");
const searchResultsCount = document.querySelector("#search-results-count");
const searchResults = document.querySelector("#search-results");
const activityView = document.querySelector("#activity-view");
const activityCards = document.querySelector("#activity-cards");
const activityHostFilter = document.querySelector("#activity-host-filter");
const activityResultFilter = document.querySelector("#activity-result-filter");
const activityExportButton = document.querySelector("#activity-export-button");
const activityRunsCount = document.querySelector("#activity-runs-count");
const activityRunsTable = document.querySelector("#activity-runs-table");
const activityEventsCount = document.querySelector("#activity-events-count");
const activityEventsTable = document.querySelector("#activity-events-table");
const hostView = document.querySelector("#host-view");
const hostSummaryCards = document.querySelector("#host-summary-cards");
const hostTitle = document.querySelector("#host-title");
const hostOverview = document.querySelector("#host-overview");
const hostMetrics = document.querySelector("#host-metrics");
const hostAlertsCount = document.querySelector("#host-alerts-count");
const hostAlertsTable = document.querySelector("#host-alerts-table");
const hostRunsCount = document.querySelector("#host-runs-count");
const hostRunsTable = document.querySelector("#host-runs-table");
const hostExternalAlertsCount = document.querySelector("#host-external-alerts-count");
const hostExternalAlertsTable = document.querySelector("#host-external-alerts-table");
const hostGrafanaPanels = document.querySelector("#host-grafana-panels");
const alertmanagerView = document.querySelector("#alertmanager-view");
const alertmanagerCards = document.querySelector("#alertmanager-cards");
const alertmanagerStatus = document.querySelector("#alertmanager-status");
const alertmanagerSourcesList = document.querySelector("#alertmanager-sources-list");
const alertmanagerRefreshButton = document.querySelector("#alertmanager-refresh-button");
const alertmanagerSourceForm = document.querySelector("#alertmanager-source-form");
const alertmanagerSourceUrl = document.querySelector("#alertmanager-source-url");
const alertmanagerSourceName = document.querySelector("#alertmanager-source-name");
const alertmanagerSourceStatus = document.querySelector("#alertmanager-source-status");
const settingsView = document.querySelector("#settings-view");
const metricsView = document.querySelector("#metrics-view");
const metricsDashboardTabs = document.querySelector("#metrics-dashboard-tabs");
const metricsHostSelect = document.querySelector("#metrics-host-select");
const metricsGrafanaFrame = document.querySelector("#metrics-grafana-frame");
const metricsOpenGrafana = document.querySelector("#metrics-open-grafana");
const maintenanceForm = document.querySelector("#maintenance-form");
const maintenanceSaveStatus = document.querySelector("#maintenance-save-status");
const maintenanceScope = document.querySelector("#maintenance-scope");
const maintenanceHost = document.querySelector("#maintenance-host");
const maintenanceAlert = document.querySelector("#maintenance-alert");
const maintenanceStartsAt = document.querySelector("#maintenance-starts-at");
const maintenanceEndsAt = document.querySelector("#maintenance-ends-at");
const maintenanceReason = document.querySelector("#maintenance-reason");
const maintenanceCount = document.querySelector("#maintenance-count");
const maintenanceTable = document.querySelector("#maintenance-table");
const mobileSecurityStatus = document.querySelector("#mobile-security-status");
const mobileEndpointForm = document.querySelector("#mobile-endpoint-form");
const mobileEndpointSaveStatus = document.querySelector("#mobile-endpoint-save-status");
const testPushButton = document.querySelector("#test-push-button");
const testPushStatus = document.querySelector("#test-push-status");
const fcmForm = document.querySelector("#fcm-form");
const fcmSaveStatus = document.querySelector("#fcm-save-status");
const mobilePublicScheme = document.querySelector("#mobile-public-scheme");
const mobilePublicHostname = document.querySelector("#mobile-public-hostname");
const mobilePublicPort = document.querySelector("#mobile-public-port");
const mobileServeHost = document.querySelector("#mobile-serve-host");
const mobileServePort = document.querySelector("#mobile-serve-port");
const mobileTlsEnabled = document.querySelector("#mobile-tls-enabled");
const mobileTlsCertfile = document.querySelector("#mobile-tls-certfile");
const mobileTlsKeyfile = document.querySelector("#mobile-tls-keyfile");
const mobilePublicEndpointLabel = document.querySelector("#mobile-public-endpoint-label");
const mobileApkDownloadLink = document.querySelector("#mobile-apk-download-link");
const mobileApkDownloadNote = document.querySelector("#mobile-apk-download-note");
const apiKeyForm = document.querySelector("#api-key-form");
const apiKeyName = document.querySelector("#api-key-name");
const apiKeyNotes = document.querySelector("#api-key-notes");
const apiKeyDeviceLimit = document.querySelector("#api-key-device-limit");
const apiKeyAllowedTargets = document.querySelector("#api-key-allowed-targets");
const apiKeyScopes = document.querySelector("#api-key-scopes");
const apiKeyCreateStatus = document.querySelector("#api-key-create-status");
const apiKeyCreatedPanel = document.querySelector("#api-key-created-panel");
const apiKeyCreatedValue = document.querySelector("#api-key-created-value");
const copyApiKeyButton = document.querySelector("#copy-api-key-button");
const apiKeysCount = document.querySelector("#api-keys-count");
const apiKeysTable = document.querySelector("#api-keys-table");
const mobileDevicesCount = document.querySelector("#mobile-devices-count");
const mobileDevicesTable = document.querySelector("#mobile-devices-table");
const agentsSettingsForm = document.querySelector("#agents-settings-form");
const agentsSettingsSaveStatus = document.querySelector("#agents-settings-save-status");
const agentsModelGrid = document.querySelector("#agents-model-grid");
const globalAgentCooldown = document.querySelector("#global-agent-cooldown");
const agentCallsCount = document.querySelector("#agent-calls-count");
const agentCallsTable = document.querySelector("#agent-calls-table");
const pipelineSettingsForm = document.querySelector("#pipeline-settings-form");
const pipelineSaveStatus = document.querySelector("#pipeline-save-status");
const pipelineEnabled = document.querySelector("#pipeline-enabled");
const pipelineAnalysisModel = document.querySelector("#pipeline-analysis-model");
const pipelineFixModel = document.querySelector("#pipeline-fix-model");
const checkSettingsCount = document.querySelector("#check-settings-count");
const checkSettingsTable = document.querySelector("#check-settings-table");

let latestReport = null;
let selectedAlertId = null;
let sidebarStateFilter = "all";
let activeTab = "status";
let activeSettingsTab = "datasources";
let activePage = "home";
let currentSearchQuery = "";
let selectedHostName = null;
let mobileAdminOverview = null;
let activityHostFilterValue = "";
let activityResultFilterValue = "";
let isCreatingAlert = false;
let alertAutosaveTimer = null;
let alertAutosaveInFlight = false;
const hostAutosaveTimers = new Map();
let alertFormDirty = false;
let hostFormDirty = false;
let notificationsOpen = false;

const severityMap = {
  critical: "Critical",
  high: "High",
  warning: "Warning",
  info: "Info",
};

function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
}

function formatDateTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

function formatRelativeTime(value) {
  if (!value) return "Never";
  const seconds = Math.max(0, Math.round((Date.now() - new Date(value).getTime()) / 1000));
  if (seconds < 60) return `${seconds} sec ago`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)} hours ago`;
  return `${Math.round(seconds / 86400)} days ago`;
}

function resultClass(result) {
  if (result === "pass" || result === "fixed") return "ok";
  if (result === "failed" || result === "fix_failed") return "bad";
  return "warn";
}

function resultLabel(result) {
  return result.replace("_", " ");
}

function iconForAlert(item) {
  if (item.statusClass === "ok") return "✓";
  if (item.statusClass === "bad") return "!";
  return "•";
}

function getAlertCatalog(report) {
  return report.alert_rules || [];
}

function buildAlertPath(alertId, tab) {
  if (!alertId) return "/";
  if (tab === "config") return `/alerts/${alertId}/edit`;
  if (tab === "triggers") return `/alerts/${alertId}/edit/triggers`;
  if (tab === "actions") return `/alerts/${alertId}/edit/actions`;
  if (tab === "targets") return `/alerts/${alertId}/targets`;
  return `/alerts/${alertId}/status`;
}

function buildSearchPath(query) {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const suffix = params.toString();
  return suffix ? `/search?${suffix}` : "/search";
}

function buildSettingsPath() {
  return "/settings";
}

function buildHostPath(hostName) {
  return `/hosts/${encodeURIComponent(hostName)}`;
}

function buildActivityPath() {
  return "/activity";
}

function readRoute() {
  const url = new URL(window.location.href);
  const parts = window.location.pathname.split("/").filter(Boolean);
  if (!parts.length) {
    activePage = "home";
    currentSearchQuery = "";
    return;
  }
  if (parts[0] === "search") {
    activePage = "search";
    currentSearchQuery = url.searchParams.get("q") || "";
    globalSearchInput.value = currentSearchQuery;
    return;
  }
  if (parts[0] === "activity") {
    activePage = "activity";
    return;
  }
  if (parts[0] === "rules") {
    activePage = "rules";
    // /rules/new and /rules/<id>/edit open the editor on a shareable URL.
    if (parts[1] === "new") pendingRuleEdit = { mode: "new" };
    else if (parts[1] && (parts[2] === "edit" || parts.length === 2)) pendingRuleEdit = { mode: "edit", id: decodeURIComponent(parts[1]) };
    else pendingRuleEdit = null;
    return;
  }
  if (parts[0] === "observability") {
    activePage = "metrics";
    return;
  }
  if (parts[0] === "settings") {
    activePage = "settings";
    return;
  }
  if (parts[0] === "alertmanager") {
    activePage = "alertmanager";
    return;
  }
  if (parts[0] === "hosts") {
    activePage = "host";
    selectedHostName = decodeURIComponent(parts[1] || "");
    return;
  }
  if (parts[0] === "alerts") {
    activePage = "alert";
    selectedAlertId = parts[1] || selectedAlertId;
    if (parts[2] === "edit" && parts[3] === "triggers") activeTab = "triggers";
    else if (parts[2] === "edit" && parts[3] === "actions") activeTab = "actions";
    else if (parts[2] === "edit") activeTab = "config";
    else if (parts[2] === "targets" || parts[2] === "hosts") activeTab = "targets";
    else activeTab = "status";
    return;
  }
  activePage = "home";
}

function syncRoute(push = true) {
  let path = "/";
  if (activePage === "search") path = buildSearchPath(currentSearchQuery);
  else if (activePage === "rules") path = ruleFormState ? (ruleFormState.id ? `/rules/${encodeURIComponent(ruleFormState.id)}/edit` : "/rules/new") : "/rules";
  else if (activePage === "metrics") path = "/observability";
  else if (activePage === "activity") path = buildActivityPath();
  else if (activePage === "settings") path = buildSettingsPath();
  else if (activePage === "alertmanager") path = "/alertmanager";
  else if (activePage === "host" && selectedHostName) path = buildHostPath(selectedHostName);
  else if (activePage === "alert" && selectedAlertId) path = buildAlertPath(selectedAlertId, activeTab);
  const current = `${window.location.pathname}${window.location.search}`;
  if (current === path) return;
  if (push) window.history.pushState({}, "", path);
  else window.history.replaceState({}, "", path);
}

function getAlertGroups(report) {
  const catalogByName = Object.fromEntries(getAlertCatalog(report).map((rule) => [rule.name, rule]));
  const grouped = new Map();

  (report.checks || []).forEach((check) => {
    const current = grouped.get(check.name) || {
      id: catalogByName[check.name]?.id || check.name,
      name: check.name,
      statusClass: "ok",
      statusText: "OK",
      description: check.description,
      checks: [],
      failingCount: 0,
      fixedCount: 0,
      passCount: 0,
      targets: new Set(),
      lastTimestamp: report.timestamp,
      config: catalogByName[check.name] || null,
      isPaused: false,
      pausedTargets: 0,
      pauseReason: "",
      pausedAt: null,
      activeTargets: 0,
      latestDetail: "",
      latestAgent: null,
      consecutiveFailures: 0,
      realState: "ok",
      isUnderMaintenance: false,
      maintenanceReason: "",
      maintenanceUntil: null,
    };

    current.checks.push(check);
    current.targets.add(check.target);
    current.latestDetail = check.detail || current.latestDetail;
    current.latestAgent = check.agent_used || current.latestAgent;
    current.consecutiveFailures = Math.max(current.consecutiveFailures, Number(check.alert_state?.consecutive_failures || 0));
    if (check.narrative) current.narrative = check.narrative;
    if (check.human_state && check.human_state !== "ok") current.human_state = check.human_state;

    if (check.alert_state?.maintenance_active) {
      current.isUnderMaintenance = true;
      current.maintenanceReason = check.alert_state.maintenance_reason || current.maintenanceReason || "";
      current.maintenanceUntil = check.alert_state.maintenance_until || current.maintenanceUntil || null;
    }

    if (check.alert_state?.schedule_paused) {
      current.isPaused = true;
      current.pausedTargets += 1;
      current.pauseReason = check.alert_state.schedule_pause_reason || current.pauseReason;
      current.pausedAt = check.alert_state.schedule_paused_at || current.pausedAt;
      current.realState = "idle";
      current.statusClass = "warn";
      current.statusText = "Idle";
    } else if (check.alert_state?.status === "firing" || check.alert_state?.status === "pending") {
      current.activeTargets += 1;
      current.realState = "failing";
      current.statusClass = "bad";
      current.statusText = check.alert_state?.status === "pending" ? "Pending" : "Failing";
    }

    if (check.result === "fix_failed" || check.result === "failed") {
      current.failingCount += 1;
    } else if (check.result === "fixed" && current.statusClass === "ok") {
      current.statusClass = "ok";
      current.statusText = "Recovered";
      current.fixedCount += 1;
    } else {
      current.passCount += 1;
    }

    grouped.set(check.name, current);
  });

  return [...grouped.values()]
    .map((item) => ({
      ...item,
      targets: [...item.targets],
      subtitle:
        item.realState === "idle"
          ? `Idle until rearm on ${item.pausedTargets} target${item.pausedTargets === 1 ? "" : "s"}`
          : item.realState === "failing"
            ? `${item.activeTargets} target${item.activeTargets === 1 ? "" : "s"} failing`
            : item.fixedCount > 0
              ? `Recovered ${formatRelativeTime(item.lastTimestamp)}`
              : `Last ${formatRelativeTime(item.lastTimestamp)}`,
    }))
    .sort((a, b) => {
      const rank = { failing: 0, idle: 1, ok: 2 };
      return (rank[a.realState] ?? 9) - (rank[b.realState] ?? 9) || a.name.localeCompare(b.name);
    });
}

function getSelectedAlert(report) {
  const alerts = getAlertGroups(report);
  if (!alerts.length) return null;
  if (!selectedAlertId || !alerts.find((item) => item.id === selectedAlertId)) {
    selectedAlertId = alerts.find((item) => item.statusClass !== "ok")?.id || alerts[0].id;
  }
  return alerts.find((item) => item.id === selectedAlertId) || alerts[0];
}

function getSelectedHost(report) {
  const hosts = report.host_catalog || {};
  const hostNames = Object.keys(hosts);
  if (!hostNames.length) return null;
  if (!selectedHostName || !hosts[selectedHostName]) {
    selectedHostName = hostNames[0];
  }
  return { name: selectedHostName, config: hosts[selectedHostName] || {} };
}

function getHistoryForAlert(report, alertName) {
  return (report.history?.checks || [])
    .filter((item) => item.name === alertName)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

function getHistoryForHost(report, hostName) {
  return (report.history?.checks || [])
    .filter((item) => item.target === hostName)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

function getDailySeries(entries) {
  const days = [];
  const now = new Date();
  for (let index = 6; index >= 0; index -= 1) {
    const day = new Date(now);
    day.setHours(0, 0, 0, 0);
    day.setDate(day.getDate() - index);
    days.push(day);
  }

  return days.map((day) => {
    const key = day.toISOString().slice(0, 10);
    const dayEntries = entries.filter((item) => item.timestamp.slice(0, 10) === key);
    const successCount = dayEntries.filter((item) => item.success).length;
    const failureCount = dayEntries.filter((item) => !item.success).length;
    const total = dayEntries.length;
    return {
      label: day.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      executions: total,
      successRate: total ? Math.round((successCount / total) * 100) : 100,
      failureRate: total ? Math.round((failureCount / total) * 100) : 0,
    };
  });
}

function csvEscape(value) {
  const text = String(value ?? "");
  if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function withinLastHours(timestamp, hours) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return false;
  return (Date.now() - date.getTime()) <= hours * 60 * 60 * 1000;
}

function parseFirstNumber(value) {
  const text = String(value ?? "");
  const match = text.match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function getCurrentTokenUsage(report) {
  return (report.checks || []).reduce((sum, item) => sum + Number(item.token_usage?.total_tokens || 0), 0);
}

function renderStatusBanner(alerts) {
  if (!dashboardStatusBanner) return;
  const okCount = alerts.filter((item) => item.realState === "ok").length;
  const actingCount = alerts.filter((item) => item.human_state === "acting" || (item.realState === "failing" && item.human_state !== "needs_you")).length;
  const needsCount = alerts.filter((item) => item.human_state === "needs_you" || item.realState === "idle").length;
  const worstState = needsCount > 0 ? "fail" : actingCount > 0 ? "warn" : "ok";
  const segments = [
    { count: okCount, label: "OK", tone: "ok" },
    { count: actingCount, label: "ACTING", tone: "warn" },
    { count: needsCount, label: "NEEDS YOU", tone: "fail" },
  ].filter((s) => s.count > 0 || s.tone === "ok");
  dashboardStatusBanner.className = `status-banner status-banner--${worstState}`;
  dashboardStatusBanner.innerHTML = segments.map((s) => `
    <span class="status-banner-segment status-banner-segment--${s.tone}">
      <span class="status-banner-dot"></span>
      <span class="status-banner-count">${s.count}</span>
      <span class="status-banner-label">${s.label}</span>
    </span>
  `).join('<span class="status-banner-sep">·</span>');
}

let lastDashboardFrameUrl = "";
// The dashboard landing now embeds the Grafana "overview" dashboard instead of
// the old hand-rolled SVG charts (those metrics live in Grafana now). The full
// set of dashboards stays in the Observability tab.
function renderDashboardOverviewFrame() {
  if (!dashboardGrafanaFrame) return;
  const overview = GRAFANA_DASHBOARDS.find((d) => d.uid === "rootcause-overview") || GRAFANA_DASHBOARDS[0];
  const url = buildMetricsUrl(overview, { kiosk: true });
  if (url !== lastDashboardFrameUrl) {
    dashboardGrafanaFrame.src = url;
    lastDashboardFrameUrl = url;
  }
  if (dashboardOpenGrafana) dashboardOpenGrafana.href = buildMetricsUrl(overview, { kiosk: false });
}

function renderHomeDashboard(report) {
  const alerts = getAlertGroups(report);
  const externalAlerts = getExternalAlerts(report);
  const failing = alerts.filter((item) => item.realState === "failing");
  const idle = alerts.filter((item) => item.realState === "idle");
  renderStatusBanner(alerts);
  const tokenTotal = getCurrentTokenUsage(report);
  const stats = [
    { label: "Failing", value: String(failing.length), tone: "bad" },
    { label: "Idle", value: String(idle.length), tone: "warn" },
    { label: "Tokens This Run", value: String(tokenTotal), tone: "ok" },
    { label: "Agents Available", value: String((report.agents || []).filter((item) => item.available).length), tone: "ok" },
  ];
  dashboardCards.innerHTML = stats.map((item) => `
    <article class="stat-card panel dashboard-card ${item.tone}">
      <label>${item.label}</label>
      <span class="metric">${item.value}</span>
    </article>
  `).join("");
  renderDashboardOverviewFrame();
  const rows = alerts.filter((item) => item.realState !== "ok");
  dashboardAlertsTable.innerHTML = rows.length ? rows.map((item) => {
    const narrative = item.narrative || {};
    const needsYou = item.human_state === "needs_you" || item.realState === "idle";
    const acting = item.human_state === "acting" || item.realState === "failing";
    const stateClass = needsYou ? "fix_failed" : acting ? "failed" : "pass";
    const stateLabel = needsYou ? "NEEDS YOU" : acting ? "ACTING" : item.statusText;
    const detailText = narrative.what_you_should_do || item.latestDetail || item.description || "-";
    return `<tr data-alert-id="${escapeAttr(item.id)}">
      <td>
        <strong>${escapeHtml(item.name)}</strong>
        ${item.isUnderMaintenance ? '<br><span class="result-pill maintenance">Maintenance</span>' : ""}
      </td>
      <td><span class="result-pill ${stateClass}">${escapeHtml(stateLabel)}</span></td>
      <td>${escapeHtml(item.targets.join(", "))}</td>
      <td>${escapeHtml(item.latestAgent || "-")}</td>
      <td><small>${escapeHtml(detailText.slice(0, 120))}</small></td>
      <td>${renderQuickActionGroup(item)}</td>
    </tr>`;
  }).join("") : '<tr><td colspan="6" class="empty">No failing or idle alerts.</td></tr>';
  dashboardAlertsTable.querySelectorAll("[data-alert-id]").forEach((row) => {
    row.addEventListener("click", () => {
      if (row.dataset.ignoreRowClick === "true") return;
      selectedAlertId = row.dataset.alertId;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
  attachQuickActionHandlers(dashboardAlertsTable, report);

  const sourceErrors = (report.external_sources || []).filter((item) => !item.ok);
  externalAlertsCount.textContent = sourceErrors.length
    ? `${externalAlerts.length} alerts · ${sourceErrors.length} source error${sourceErrors.length === 1 ? "" : "s"}`
    : `${externalAlerts.length} alerts`;
  externalAlertsTable.innerHTML = externalAlerts.length ? externalAlerts.map((item) => `
    <tr>
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.host || "-")}</td>
      <td>${escapeHtml(item.severity || "-")}</td>
      <td><span class="result-pill ${externalAlertStateClass(item)}">${escapeHtml(item.status_text || item.state || "-")}</span></td>
      <td>${escapeHtml(item.summary || item.description || "-")}</td>
      <td>${item.silenced ? '<span class="caption">silenced</span>' : renderExternalAlertActionGroup(item)}</td>
    </tr>
  `).join("") : `<tr><td colspan="6" class="empty">${
    sourceErrors.length
      ? `Alertmanager unavailable: ${escapeHtml(sourceErrors.map((item) => item.error).join(" | "))}`
      : "No external alerts from Alertmanager."
  }</td></tr>`;
  attachExternalAlertActionHandlers(externalAlertsTable, report);
}

function buildSearchResults(report, query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const results = [];
  const catalogByName = Object.fromEntries((report.alert_rules || []).map((rule) => [rule.name, rule]));
  (report.alert_rules || []).forEach((rule) => {
    const haystack = `${rule.name} ${rule.description} ${rule.fix_prompt || ""} ${(rule.targets || []).join(" ")}`.toLowerCase();
    if (haystack.includes(q)) {
      results.push({
        kind: "Alert",
        title: rule.name,
        body: rule.description || "",
        meta: `targets: ${(rule.targets || []).join(", ")}`,
        action: "alert",
        alertId: rule.id || rule.name,
      });
    }
    if ((rule.fix_prompt || "").toLowerCase().includes(q)) {
      results.push({
        kind: "Prompt",
        title: `${rule.name} fix prompt`,
        body: (rule.fix_prompt || "").slice(0, 260),
        meta: "alert remediation prompt",
        action: "alert",
        alertId: rule.id || rule.name,
      });
    }
  });
  Object.entries(report.host_catalog || {}).forEach(([name, host]) => {
    const haystack = `${name} ${host.address || ""} ${host.ssh_user || ""} ${host.labels?.role || ""} ${host.prometheus_url || ""} ${host.alertmanager_url || ""}`.toLowerCase();
    if (haystack.includes(q)) {
      results.push({
        kind: "Host",
        title: name,
        body: host.address || "-",
        meta: `${host.connection || "ssh"} · ${host.ssh_user || "-"}`,
        action: "host",
        hostName: name,
      });
    }
  });
  (report.history?.checks || []).forEach((item) => {
    const haystack = `${item.name} ${item.detail || ""} ${item.agent_used || ""} ${item.target || ""}`.toLowerCase();
    if (haystack.includes(q)) {
      results.push({
        kind: "Execution",
        title: `${item.name} on ${item.target}`,
        body: item.detail || item.result || "-",
        meta: formatDateTime(item.timestamp),
        action: "alert",
        alertId: catalogByName[item.name]?.id || item.name,
      });
    }
  });
  getExternalAlerts(report).forEach((item) => {
    const haystack = `${item.name} ${item.host || ""} ${item.summary || ""} ${item.description || ""} ${item.severity || ""}`.toLowerCase();
    if (haystack.includes(q)) {
      results.push({
        kind: "External",
        title: `${item.name}${item.host ? ` on ${item.host}` : ""}`,
        body: item.summary || item.description || "-",
        meta: `alertmanager · ${item.status_text || item.state || "-"} · ${item.severity || "-"}`,
        action: item.host ? "host" : "",
        hostName: item.host || "",
      });
    }
  });
  return results.slice(0, 80);
}

function renderSearchResults(report) {
  const results = buildSearchResults(report, currentSearchQuery);
  searchResultsTitle.textContent = currentSearchQuery ? `Results for "${currentSearchQuery}"` : "Results";
  searchResultsCount.textContent = `${results.length} results`;
  searchResults.innerHTML = results.length ? results.map((item) => `
    <article class="search-result-card" ${item.action ? `data-action="${escapeAttr(item.action)}"` : ""} ${item.alertId ? `data-alert-id="${escapeAttr(item.alertId)}"` : ""} ${item.hostName ? `data-host-name="${escapeAttr(item.hostName)}"` : ""}>
      <span class="code-pill">${escapeHtml(item.kind)}</span>
      <h4>${escapeHtml(item.title)}</h4>
      <p>${escapeHtml(item.body)}</p>
      <small>${escapeHtml(item.meta)}</small>
    </article>
  `).join("") : '<div class="empty">No results for this search.</div>';
  searchResults.querySelectorAll("[data-action='alert'][data-alert-id]").forEach((node) => {
    node.addEventListener("click", () => {
      selectedAlertId = node.dataset.alertId;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
  searchResults.querySelectorAll("[data-action='host']").forEach((node) => {
    node.addEventListener("click", () => {
      selectedHostName = node.dataset.hostName;
      activePage = "host";
      notificationsOpen = false;
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
}

function renderQuickActionGroup(alert) {
  return `
    <div class="quick-actions" data-ignore-row-click="true">
      <button class="secondary-button quick-action-button" type="button" data-quick-action="ack" data-alert-id="${escapeAttr(alert.id)}" data-alert-name="${escapeAttr(alert.name)}">Ack</button>
      <button class="secondary-button quick-action-button" type="button" data-quick-action="silence" data-alert-id="${escapeAttr(alert.id)}" data-alert-name="${escapeAttr(alert.name)}">Silence</button>
      <button class="secondary-button quick-action-button" type="button" data-quick-action="rerun" data-alert-id="${escapeAttr(alert.id)}" data-alert-name="${escapeAttr(alert.name)}">Rerun</button>
    </div>
  `;
}

function renderExternalAlertActionGroup(alert) {
  return `
    <div class="quick-actions" data-ignore-row-click="true">
      <button class="secondary-button external-silence-button" type="button"
        data-fingerprint="${escapeAttr(alert.fingerprint || "")}"
        data-alertmanager-url="${escapeAttr(alert.alertmanager_url || "")}"
        data-alert-name="${escapeAttr(alert.name || "")}">
        Silence
      </button>
    </div>
  `;
}

async function runQuickAlertAction(action, alertId, alertName) {
  const routeByAction = {
    ack: "/api/alert/ack",
    silence: "/api/alert/silence",
    rerun: "/api/alert/rerun",
  };
  const route = routeByAction[action];
  if (!route) throw new Error(`unknown action: ${action}`);
  const payload = { id: alertId, name: alertName };
  if (action === "silence") {
    payload.minutes = 60;
    payload.reason = "Silenced from web";
  }
  const response = await fetch(route, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `failed to ${action}`);
  if (action === "rerun") {
    const tone = data.ran === 0 ? "warning" : (data.results || []).some((r) => r.result !== "pass" && r.result !== "fixed") ? "warning" : "success";
    showToast(data.message || "Re-run completed", tone);
  } else {
    showToast(data.message || `${action} done`, "success");
  }
  await loadStatus(true);
  return data;
}

async function runExternalAlertSilence(fingerprint, alertmanagerUrl, alertName) {
  const response = await fetch("/api/external-alert/silence", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fingerprint,
      alertmanager_url: alertmanagerUrl,
      minutes: 60,
      reason: `Silenced from RootCause web for external alert ${alertName || ""}`.trim(),
    }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to silence external alert");
  await loadStatus(true);
  return data;
}

function attachQuickActionHandlers(container, report) {
  container.querySelectorAll("[data-quick-action]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      event.preventDefault();
      event.stopPropagation();
      const row = button.closest("tr,[data-alert-id],.notification-item");
      if (row) row.dataset.ignoreRowClick = "true";
      const originalText = button.textContent;
      button.disabled = true;
      button.textContent = "...";
      try {
        await runQuickAlertAction(button.dataset.quickAction, button.dataset.alertId, button.dataset.alertName);
      } catch (error) {
        showToast(`${button.dataset.quickAction} failed: ${error.message}`, "error");
        if (latestReport) render(latestReport || report);
      } finally {
        button.disabled = false;
        button.textContent = originalText;
        if (row) delete row.dataset.ignoreRowClick;
      }
    });
  });
}

function attachExternalAlertActionHandlers(container, report) {
  container.querySelectorAll(".external-silence-button").forEach((button) => {
    button.addEventListener("click", async (event) => {
      event.preventDefault();
      event.stopPropagation();
      const originalText = button.textContent;
      button.disabled = true;
      button.textContent = "...";
      try {
        await runExternalAlertSilence(
          button.dataset.fingerprint,
          button.dataset.alertmanagerUrl,
          button.dataset.alertName,
        );
      } catch (error) {
        alert(error.message);
        if (latestReport) render(latestReport || report);
      } finally {
        button.disabled = false;
        button.textContent = originalText;
      }
    });
  });
}

let alertmanagerData = null;

async function loadAlertmanagerData() {
  if (alertmanagerStatus) alertmanagerStatus.textContent = "Loading...";
  try {
    const response = await fetch("/api/alertmanager/alerts", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to load");
    alertmanagerData = data;
    renderAlertmanagerView(data);
  } catch (error) {
    if (alertmanagerStatus) alertmanagerStatus.textContent = `Error: ${error.message}`;
    if (alertmanagerSourcesList) alertmanagerSourcesList.innerHTML = `<div class="empty" style="padding:14px;color:var(--red)">Failed to load: ${escapeHtml(error.message)}</div>`;
  }
}

function renderAlertmanagerView(data) {
  const sources = (data && data.sources) || [];
  if (!alertmanagerSourcesList) return;

  const totalAlerts = sources.reduce((sum, s) => sum + (s.alert_count || 0), 0);
  const firingCount = sources.reduce((sum, s) => sum + (s.alerts || []).filter((a) => a.state === "firing" && !a.silenced).length, 0);
  const silencedCount = sources.reduce((sum, s) => sum + (s.alerts || []).filter((a) => a.silenced).length, 0);

  if (alertmanagerCards) {
    const firingClass = firingCount ? "am-stat-bad" : "";
    const totalClass = totalAlerts ? "am-stat-warn" : "";
    alertmanagerCards.innerHTML = `
      <div class="am-stats-bar">
        <span class="am-stat"><strong>${sources.length}</strong> source${sources.length === 1 ? "" : "s"}</span>
        <span class="am-stat-sep">·</span>
        <span class="am-stat ${totalClass}"><strong>${totalAlerts}</strong> total</span>
        <span class="am-stat-sep">·</span>
        <span class="am-stat ${firingClass}"><strong>${firingCount}</strong> firing</span>
        <span class="am-stat-sep">·</span>
        <span class="am-stat"><strong>${silencedCount}</strong> silenced</span>
      </div>
    `;
  }

  if (alertmanagerStatus) {
    alertmanagerStatus.textContent = `${sources.length} source${sources.length === 1 ? "" : "s"} · ${totalAlerts} alert${totalAlerts === 1 ? "" : "s"}`;
  }

  if (!sources.length) {
    alertmanagerSourcesList.innerHTML = `
      <article class="panel table-panel">
        <div class="empty" style="padding:24px;text-align:center">
          No Alertmanager sources found.<br>
          <small style="color:var(--muted)">Add a URL above, or set <code>alertmanager_url</code> on a host in Targets.</small>
        </div>
      </article>
    `;
    return;
  }

  alertmanagerSourcesList.innerHTML = sources.map((source) => {
    const alerts = source.alerts || [];
    const firing = alerts.filter((a) => a.state === "firing" && !a.silenced);
    const pill = source.ok
      ? `<span class="result-pill pass">${escapeHtml(`${firing.length} firing · ${alerts.length} total`)}</span>`
      : `<span class="result-pill failed">Unreachable</span>`;

    const hostsInfo = source.hosts && source.hosts.length
      ? `· hosts: ${source.hosts.map(escapeHtml).join(", ")}`
      : "";

    let bodyHtml = "";
    if (!source.ok) {
      bodyHtml = `<div class="empty" style="padding:14px;color:var(--red)">Cannot connect: ${escapeHtml(source.error || "unknown error")}</div>`;
    } else if (!alerts.length) {
      bodyHtml = `<div class="empty" style="padding:14px">No alerts in this Alertmanager instance.</div>`;
    } else {
      const rows = alerts.map((alert) => {
        const stateClass = alert.silenced ? "maintenance" : alert.state === "firing" ? "failed" : "pass";
        const stateLabel = alert.silenced ? "silenced" : alert.state || "-";
        const sevClass = `sev-${escapeAttr((alert.severity || "unknown").toLowerCase())}`;
        const importCell = alert.imported
          ? `<span class="am-imported-badge">Imported</span>`
          : `<button class="primary-button am-import-button"
               style="padding:4px 10px;font-size:0.75rem"
               data-alertmanager-url="${escapeAttr(source.url)}"
               data-alertname="${escapeAttr(alert.name)}"
               data-severity="${escapeAttr(alert.severity || "warning")}"
               data-summary="${escapeAttr(alert.summary || alert.description || "")}"
               data-labels="${escapeAttr(JSON.stringify(alert.labels || {}))}"
               type="button">Import as check</button>`;
        return `
          <tr>
            <td><strong>${escapeHtml(alert.name)}</strong></td>
            <td><span class="sev-pill ${sevClass}">${escapeHtml(alert.severity || "-")}</span></td>
            <td><span class="result-pill ${stateClass}">${escapeHtml(stateLabel)}</span></td>
            <td>${escapeHtml(alert.host || "-")}</td>
            <td style="max-width:240px;white-space:normal;font-size:0.8rem">${escapeHtml((alert.summary || alert.description || "-").slice(0, 100))}</td>
            <td>${importCell}</td>
          </tr>
        `;
      }).join("");
      bodyHtml = `
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Alert</th>
                <th>Severity</th>
                <th>State</th>
                <th>Host</th>
                <th>Summary</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    }

    return `
      <article class="panel table-panel am-source-card">
        <div class="panel-head">
          <div>
            <p class="panel-kicker">${escapeHtml(source.autodiscovered ? "Autodiscovered from host" : "Manual source")}${source.name ? ` · ${escapeHtml(source.name)}` : ""}</p>
            <h3>${escapeHtml(source.url)}</h3>
          </div>
          <div class="header-actions">
            ${pill}
            ${source.hosts && source.hosts.length ? `<span class="caption">${escapeHtml(hostsInfo)}</span>` : ""}
            ${!source.autodiscovered ? `<button class="danger-button am-source-delete" data-url="${escapeAttr(source.url)}" type="button" style="font-size:0.78rem;padding:4px 10px">Remove</button>` : ""}
          </div>
        </div>
        ${bodyHtml}
      </article>
    `;
  }).join("");

  alertmanagerSourcesList.querySelectorAll(".am-import-button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.dataset.alertmanagerUrl;
      const alertname = btn.dataset.alertname;
      const severity = btn.dataset.severity;
      const summary = btn.dataset.summary;
      let labels = {};
      try { labels = JSON.parse(btn.dataset.labels || "{}"); } catch {}
      btn.disabled = true;
      btn.textContent = "Importing...";
      try {
        const response = await fetch("/api/alertmanager/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ alertmanager_url: url, alertname, severity, summary, labels }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Import failed");
        btn.textContent = "Imported ✓";
        btn.classList.remove("primary-button");
        btn.classList.add("secondary-button");
        btn.disabled = true;
        await loadStatus();
        await loadAlertmanagerData();
      } catch (error) {
        btn.disabled = false;
        btn.textContent = "Import as check";
        alert(`Import failed: ${error.message}`);
      }
    });
  });

  alertmanagerSourcesList.querySelectorAll(".am-source-delete").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.dataset.url;
      if (!confirm(`Remove Alertmanager source:\n${url}`)) return;
      try {
        const response = await fetch("/api/alertmanager/source/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Delete failed");
        await loadAlertmanagerData();
      } catch (error) {
        alert(`Failed to remove source: ${error.message}`);
      }
    });
  });
}

function renderGrafanaPanels(hostConfig) {
  if (!hostGrafanaPanels) return;
  const grafanaUrl = (hostConfig.grafana_url || "").replace(/\/$/, "");
  const panels = hostConfig.grafana_panels || [];
  if (!grafanaUrl || !panels.length) {
    hostGrafanaPanels.innerHTML = "";
    return;
  }
  const from = "now-1h";
  const to = "now";
  const theme = "dark";
  const items = panels.map((panel) => {
    const uid = encodeURIComponent(panel.dashboard_uid || "");
    const panelId = encodeURIComponent(panel.panel_id || 1);
    const panelFrom = encodeURIComponent(panel.from || from);
    const panelTo = encodeURIComponent(panel.to || to);
    let src = `${grafanaUrl}/d-solo/${uid}?panelId=${panelId}&theme=${theme}&from=${panelFrom}&to=${panelTo}&orgId=1&refresh=30s`;
    const vars = panel.vars || {};
    Object.keys(vars).forEach((key) => {
      src += `&var-${encodeURIComponent(key)}=${encodeURIComponent(vars[key])}`;
    });
    return `
      <div class="grafana-panel-item">
        <h4>${escapeHtml(panel.title || `Panel ${panel.panel_id}`)}</h4>
        <iframe class="grafana-panel-frame" src="${escapeAttr(src)}" loading="lazy" allowfullscreen></iframe>
      </div>
    `;
  }).join("");
  hostGrafanaPanels.innerHTML = `
    <article class="panel grafana-panels-section">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">Grafana</p>
          <h3>Live Metrics</h3>
        </div>
        <a class="secondary-button" href="${escapeAttr(grafanaUrl)}" target="_blank" rel="noopener">Open Grafana</a>
      </div>
      <div class="grafana-panels-grid">${items}</div>
    </article>
  `;
}

// --- Embedded Grafana "Metrics" section -----------------------------------
// Grafana instance labels are set in prometheus.yml (the "instance" label on
// each scrape target). Add the instances you actually scrape here.
const GRAFANA_INSTANCES = [
  { label: "Localhost", value: "localhost" },
];
const GRAFANA_DASHBOARDS = [
  { uid: "rootcause-overview", title: "Overview", hostScoped: false },
  { uid: "rootcause-ai-tokens", title: "IA / Tokens", hostScoped: false },
  { uid: "rootcause-node", title: "Sistema", hostScoped: true },
  { uid: "rootcause-temps", title: "Temperaturas", hostScoped: true, compare: true },
  { uid: "rootcause-containers", title: "Contenedores", hostScoped: true,
    instances: [{ label: "Localhost", value: "localhost" }] },
];
const COMPARE_OPTION = { label: "Comparar (ambos)", value: "__all__" };

function metricsInstanceOptions(dashboard) {
  const base = dashboard.instances || GRAFANA_INSTANCES;
  return dashboard.compare ? [COMPARE_OPTION, ...base] : base;
}
let activeMetricsDashboard = GRAFANA_DASHBOARDS[0].uid;
let activeMetricsInstance = GRAFANA_INSTANCES[0].value;
let metricsTabsBuilt = false;
let lastMetricsFrameUrl = "";

function grafanaBaseUrl() {
  // Grafana is served on the workstation at :3000 (anonymous). Prefer the URL
  // configured in the host catalog (Settings → Hosts) so the iframes point at a
  // host reachable from wherever the UI is opened. This matters for a remote
  // browser reaching RootCause through an SSH tunnel: window.location.hostname is
  // 127.0.0.1 there, which would resolve to the *remote* machine, not the
  // workstation where Grafana actually runs.
  const hosts = (latestReport && latestReport.host_catalog) || {};
  const configured = (hosts.localhost && hosts.localhost.grafana_url)
    || Object.values(hosts).map((h) => h && h.grafana_url).find(Boolean);
  if (configured) return configured.replace(/\/$/, "");
  return `http://${window.location.hostname || "127.0.0.1"}:3000`;
}

function getMetricsDashboard() {
  return GRAFANA_DASHBOARDS.find((d) => d.uid === activeMetricsDashboard) || GRAFANA_DASHBOARDS[0];
}

function buildMetricsUrl(dashboard, { kiosk } = { kiosk: true }) {
  const base = grafanaBaseUrl();
  const params = new URLSearchParams();
  if (kiosk) params.set("kiosk", "");
  params.set("theme", "dark");
  params.set("refresh", "30s");
  params.set("from", "now-3h");
  params.set("to", "now");
  params.set("orgId", "1");
  let varQs = "";
  if (dashboard.hostScoped) {
    if (activeMetricsInstance === COMPARE_OPTION.value) {
      // Compare mode: pass every host so dashboards overlay both instances.
      varQs = (dashboard.instances || GRAFANA_INSTANCES)
        .map((i) => `&var-instance=${encodeURIComponent(i.value)}`).join("");
    } else {
      varQs = `&var-instance=${encodeURIComponent(activeMetricsInstance)}`;
    }
  }
  // Grafana resolves dashboards by uid; the slug segment is cosmetic.
  // URLSearchParams encodes the bare "kiosk" flag as "kiosk=" — Grafana accepts it.
  return `${base}/d/${encodeURIComponent(dashboard.uid)}/rootcause?${params.toString()}${varQs}`;
}

function buildMetricsTabs() {
  if (!metricsDashboardTabs) return;
  metricsDashboardTabs.innerHTML = GRAFANA_DASHBOARDS.map((d) =>
    `<button class="metrics-tab ${d.uid === activeMetricsDashboard ? "is-active" : ""}" type="button" data-dashboard="${escapeAttr(d.uid)}">${escapeHtml(d.title)}</button>`
  ).join("");
  metricsDashboardTabs.querySelectorAll(".metrics-tab").forEach((node) => {
    node.addEventListener("click", () => {
      activeMetricsDashboard = node.dataset.dashboard;
      renderMetricsView();
    });
  });
  metricsTabsBuilt = true;
}

function renderMetricsView() {
  if (!metricsView) return;
  if (!metricsTabsBuilt) buildMetricsTabs();
  metricsDashboardTabs.querySelectorAll(".metrics-tab").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.dashboard === activeMetricsDashboard);
  });

  const dashboard = getMetricsDashboard();
  const instances = metricsInstanceOptions(dashboard);
  if (dashboard.hostScoped) {
    if (!instances.some((i) => i.value === activeMetricsInstance)) {
      activeMetricsInstance = instances[0].value;
    }
    metricsHostSelect.style.display = "";
    metricsHostSelect.innerHTML = instances.map((i) =>
      `<option value="${escapeAttr(i.value)}" ${i.value === activeMetricsInstance ? "selected" : ""}>${escapeHtml(i.label)}</option>`
    ).join("");
  } else {
    metricsHostSelect.style.display = "none";
  }

  if (metricsOpenGrafana) metricsOpenGrafana.href = buildMetricsUrl(dashboard, { kiosk: false });

  // Only (re)assign the iframe src when it actually changes, so the periodic
  // status poll doesn't reload Grafana on every tick.
  const url = buildMetricsUrl(dashboard, { kiosk: true });
  if (url !== lastMetricsFrameUrl) {
    metricsGrafanaFrame.src = url;
    lastMetricsFrameUrl = url;
  }
}

if (metricsHostSelect) {
  metricsHostSelect.addEventListener("change", () => {
    activeMetricsInstance = metricsHostSelect.value;
    renderMetricsView();
  });
}

// Per-check Grafana panels embedded in the check detail page (rootcause-check
// dashboard, filtered by var-check). Replaces the old SVG trend charts.
const checkGrafanaPanelsEl = document.querySelector("#check-grafana-panels");
const CHECK_GRAFANA_PANELS = [
  { title: "Estado actual", panel_id: 1 },
  { title: "Fallos consecutivos", panel_id: 2 },
  { title: "Ejecuciones vs fallos (por hora)", panel_id: 4 },
  { title: "Auto-fixes (por hora)", panel_id: 5 },
];
let lastCheckPanelsKey = "";

function renderCheckGrafanaPanels(selected) {
  if (!checkGrafanaPanelsEl || !selected) return;
  // Only rebuild when the selected check changes, so the status poll doesn't
  // reload the iframes on every tick.
  if (selected.name === lastCheckPanelsKey) return;
  lastCheckPanelsKey = selected.name;

  const base = grafanaBaseUrl();
  const checkVar = encodeURIComponent(selected.name);
  const items = CHECK_GRAFANA_PANELS.map((p) => {
    const src = `${base}/d-solo/rootcause-check/rootcause?panelId=${p.panel_id}&theme=dark&from=now-7d&to=now&orgId=1&refresh=30s&var-check=${checkVar}`;
    return `
      <div class="grafana-panel-item">
        <h4>${escapeHtml(p.title)}</h4>
        <iframe class="grafana-panel-frame" src="${escapeAttr(src)}" loading="lazy" allowfullscreen></iframe>
      </div>`;
  }).join("");
  const openUrl = `${base}/d/rootcause-check/rootcause?var-check=${checkVar}`;
  checkGrafanaPanelsEl.innerHTML = `
    <article class="panel grafana-panels-section">
      <div class="panel-head">
        <div>
          <p class="panel-kicker">Grafana</p>
          <h3>Métricas del check</h3>
        </div>
        <a class="secondary-button" href="${escapeAttr(openUrl)}" target="_blank" rel="noopener">Abrir en Grafana</a>
      </div>
      <div class="grafana-panels-grid">${items}</div>
    </article>`;
}

function renderHostView(report) {
  const selected = getSelectedHost(report);
  if (!selected) {
    hostSummaryCards.innerHTML = '<div class="empty">No hosts configured.</div>';
    hostOverview.innerHTML = '<div class="empty">No host selected.</div>';
    hostMetrics.innerHTML = '<div class="empty">No data.</div>';
    hostAlertsTable.innerHTML = '<tr><td colspan="4" class="empty">No alerts assigned.</td></tr>';
    hostRunsTable.innerHTML = '<tr><td colspan="4" class="empty">No executions yet.</td></tr>';
    hostExternalAlertsCount.textContent = "0 alerts";
    hostExternalAlertsTable.innerHTML = '<tr><td colspan="6" class="empty">No external alerts.</td></tr>';
    return;
  }
  const { name, config } = selected;
  const checks = (report.checks || []).filter((item) => item.target === name);
  const alertGroups = getAlertGroups(report).filter((item) => item.targets.includes(name));
  const runs = getHistoryForHost(report, name).slice(0, 10);
  const externalAlerts = getExternalAlerts(report).filter((item) => item.host === name);
  const failing = alertGroups.filter((item) => item.realState === "failing").length;
  const idle = alertGroups.filter((item) => item.realState === "idle").length;
  const ok = alertGroups.filter((item) => item.realState === "ok").length;

  hostTitle.textContent = name;
  hostSummaryCards.innerHTML = [
    { label: "Failing", value: String(failing), tone: "bad" },
    { label: "Idle", value: String(idle), tone: "warn" },
    { label: "OK", value: String(ok), tone: "ok" },
    { label: "Checks", value: String(checks.length), tone: "ok" },
  ].map((item) => `
    <article class="stat-card panel dashboard-card ${item.tone}">
      <label>${item.label}</label>
      <span class="metric">${item.value}</span>
    </article>
  `).join("");

  hostOverview.innerHTML = `
    <div class="dashboard-metric-row"><strong>Address</strong><span>${escapeHtml(config.address || "-")}</span><small>${escapeHtml(config.connection || "ssh")}</small></div>
    <div class="dashboard-metric-row"><strong>User</strong><span>${escapeHtml(config.ssh_user || "-")}</span><small>${escapeHtml(`port ${config.ssh_port || 22}`)}</small></div>
    <div class="dashboard-metric-row"><strong>Role</strong><span>${escapeHtml(config.labels?.role || "-")}</span><small>${escapeHtml(config.enabled === false ? "disabled" : "enabled")}</small></div>
    <div class="dashboard-metric-row"><strong>Prometheus</strong><span>${escapeHtml(config.prometheus_url || "-")}</span><small>${escapeHtml(config.workdir || "")}</small></div>
    <div class="dashboard-metric-row"><strong>Alertmanager</strong><span>${escapeHtml(config.alertmanager_url || "-")}</span><small>${escapeHtml(`${externalAlerts.length} external alert${externalAlerts.length === 1 ? "" : "s"}`)}</small></div>
    ${config.grafana_url ? `<div class="dashboard-metric-row"><strong>Grafana</strong><span><a href="${escapeAttr(config.grafana_url)}" target="_blank" rel="noopener">${escapeHtml(config.grafana_url)}</a></span><small>${escapeHtml(`${(config.grafana_panels || []).length} panel${(config.grafana_panels || []).length === 1 ? "" : "s"} configured`)}</small></div>` : ""}
  `;

  hostMetrics.innerHTML = checks.length ? checks.slice().sort((a, b) => a.name.localeCompare(b.name)).map((item) => `
    <div class="dashboard-metric-row">
      <strong>${escapeHtml(item.name)}</strong>
      <span>${escapeHtml(item.result || "-")}</span>
      <small>${escapeHtml(item.detail || "-")}</small>
    </div>
  `).join("") : '<div class="empty">No checks found for this host.</div>';

  hostAlertsCount.textContent = `${alertGroups.length} alerts`;
  hostAlertsTable.innerHTML = alertGroups.length ? alertGroups.map((item) => `
    <tr data-alert-id="${escapeAttr(item.id)}">
      <td>${escapeHtml(item.name)}</td>
      <td>
        <span class="result-pill ${item.realState === "failing" ? "failed" : item.realState === "idle" ? "fix_failed" : "pass"}">${escapeHtml(item.statusText)}</span>
        ${item.isUnderMaintenance ? '<span class="result-pill maintenance" title="Under maintenance">Maintenance</span>' : ""}
      </td>
      <td>${escapeHtml(item.latestDetail || item.description || "-")}</td>
      <td>${renderQuickActionGroup(item)}</td>
    </tr>
  `).join("") : '<tr><td colspan="4" class="empty">No alerts assigned to this host.</td></tr>';
  hostAlertsTable.querySelectorAll("[data-alert-id]").forEach((row) => {
    row.addEventListener("click", () => {
      if (row.dataset.ignoreRowClick === "true") return;
      selectedAlertId = row.dataset.alertId;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
  attachQuickActionHandlers(hostAlertsTable, report);

  hostRunsCount.textContent = `${runs.length} runs`;
  hostRunsTable.innerHTML = runs.length ? runs.map((item) => `
    <tr data-alert-name="${escapeAttr(item.name)}">
      <td>${formatDateTime(item.timestamp)}</td>
      <td>${escapeHtml(item.name)}</td>
      <td><span class="result-pill ${escapeAttr(item.result)}">${escapeHtml(resultLabel(item.result))}</span></td>
      <td>${escapeHtml(`${(item.duration_seconds || 0).toFixed(2)}s`)}</td>
    </tr>
  `).join("") : '<tr><td colspan="4" class="empty">No executions recorded for this host yet.</td></tr>';
  hostRunsTable.querySelectorAll("[data-alert-name]").forEach((row) => {
    row.addEventListener("click", () => {
      const alert = (getAlertGroups(report) || []).find((item) => item.name === row.dataset.alertName);
      if (!alert) return;
      selectedAlertId = alert.id;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      render(report);
    });
  });

  hostExternalAlertsCount.textContent = `${externalAlerts.length} alerts`;
  hostExternalAlertsTable.innerHTML = externalAlerts.length ? externalAlerts.map((item) => `
    <tr>
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.severity || "-")}</td>
      <td><span class="result-pill ${externalAlertStateClass(item)}">${escapeHtml(item.status_text || item.state || "-")}</span></td>
      <td>${escapeHtml(formatDateTime(item.starts_at))}</td>
      <td>${escapeHtml(item.summary || item.description || "-")}</td>
      <td>${item.silenced ? '<span class="caption">silenced</span>' : renderExternalAlertActionGroup(item)}</td>
    </tr>
  `).join("") : '<tr><td colspan="6" class="empty">No Alertmanager alerts mapped to this host.</td></tr>';
  attachExternalAlertActionHandlers(hostExternalAlertsTable, report);
  renderGrafanaPanels(config);
}

function renderActivityView(report) {
  const runs = [...(report.history?.runs || [])].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  const checks = [...(report.history?.checks || [])].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  const hosts = Object.keys(report.host_catalog || {}).sort((a, b) => a.localeCompare(b));
  if (activityHostFilter) {
    const currentOptions = Array.from(activityHostFilter.options).map((option) => option.value);
    const desiredOptions = ["", ...hosts];
    if (currentOptions.join("|") !== desiredOptions.join("|")) {
      activityHostFilter.innerHTML = `
        <option value="">All hosts</option>
        ${hosts.map((host) => `<option value="${escapeAttr(host)}">${escapeHtml(host)}</option>`).join("")}
      `;
    }
    activityHostFilter.value = activityHostFilterValue;
  }
  if (activityResultFilter) {
    activityResultFilter.value = activityResultFilterValue;
  }
  const filteredChecks = checks.filter((item) => {
    if (activityHostFilterValue && item.target !== activityHostFilterValue) return false;
    if (activityResultFilterValue && item.result !== activityResultFilterValue) return false;
    return true;
  });
  const last24Runs = runs.filter((item) => withinLastHours(item.timestamp, 24));
  const last24Checks = filteredChecks.filter((item) => withinLastHours(item.timestamp, 24));
  const failed24 = last24Checks.filter((item) => ["failed", "fix_failed"].includes(item.result)).length;
  const fixed24 = last24Checks.filter((item) => item.result === "fixed").length;
  const token24 = last24Checks.reduce((sum, item) => sum + Number(item.token_total || 0), 0);

  activityCards.innerHTML = [
    { label: "Runs · 24h", value: String(last24Runs.length), tone: "ok" },
    { label: "Failures · 24h", value: String(failed24), tone: failed24 ? "bad" : "ok" },
    { label: "Fixed · 24h", value: String(fixed24), tone: fixed24 ? "ok" : "warn" },
    { label: "Tokens · 24h", value: String(token24), tone: token24 ? "warn" : "ok" },
  ].map((item) => `
    <article class="stat-card panel dashboard-card ${item.tone}">
      <label>${item.label}</label>
      <span class="metric">${item.value}</span>
    </article>
  `).join("");

  activityRunsCount.textContent = `${Math.min(runs.length, 20)} runs`;
  activityRunsTable.innerHTML = runs.length ? runs.slice(0, 20).map((item) => {
    const failed = Number(item.summary?.failed ?? 0);
    const fixed = Number(item.summary?.fixed ?? 0);
    const paused = Number(item.summary?.paused ?? 0);
    // "Evaluated" = checks actually run this cycle; fleet_total = whole fleet the
    // PASSED/FAILED columns describe. Older records lack these fields.
    const evaluated = item.evaluated;
    const fleetTotal = item.fleet_total;
    const evaluatedCell = evaluated == null
      ? "—"
      : `${evaluated}${fleetTotal != null ? ` / ${fleetTotal}` : ""}`;
    return `
    <tr>
      <td>${formatDateTime(item.timestamp)}</td>
      <td class="muted-cell">${escapeHtml(evaluatedCell)}</td>
      <td>${escapeHtml(String(item.summary?.passed ?? 0))}</td>
      <td class="${failed ? "cell-bad" : ""}">${escapeHtml(String(failed))}</td>
      <td class="${fixed ? "cell-ok" : ""}">${escapeHtml(String(fixed))}</td>
      <td class="${paused ? "cell-warn" : ""}">${escapeHtml(String(paused))}</td>
      <td>${escapeHtml(`${Number(item.duration_seconds || 0).toFixed(2)}s`)}</td>
    </tr>
  `;
  }).join("") : '<tr><td colspan="7" class="empty">No runs recorded yet.</td></tr>';

  activityEventsCount.textContent = `${Math.min(filteredChecks.length, 30)} events`;
  activityEventsTable.innerHTML = filteredChecks.length ? filteredChecks.slice(0, 30).map((item) => {
    const rule = (report.alert_rules || []).find((entry) => entry.name === item.name);
    const alertId = rule?.id || "";
    return `
      <tr ${alertId ? `data-alert-id="${escapeAttr(alertId)}"` : ""}>
        <td>${formatDateTime(item.timestamp)}</td>
        <td>${escapeHtml(item.name)}</td>
        <td>${escapeHtml(item.target || "-")}</td>
        <td><span class="result-pill ${escapeAttr(item.result)}">${escapeHtml(resultLabel(item.result))}</span></td>
        <td>${escapeHtml(String(item.token_total || 0))}</td>
        <td>${escapeHtml(`${Number(item.duration_seconds || 0).toFixed(2)}s`)}</td>
      </tr>
    `;
  }).join("") : '<tr><td colspan="6" class="empty">No execution history for this filter.</td></tr>';
  activityEventsTable.querySelectorAll("[data-alert-id]").forEach((row) => {
    row.addEventListener("click", () => {
      selectedAlertId = row.dataset.alertId;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      render(report);
    });
  });
}

function exportActivityCsv(report) {
  const checks = [...(report.history?.checks || [])]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .filter((item) => {
      if (activityHostFilterValue && item.target !== activityHostFilterValue) return false;
      if (activityResultFilterValue && item.result !== activityResultFilterValue) return false;
      return true;
    });
  const lines = [
    ["timestamp", "alert", "host", "result", "tokens", "duration_seconds"],
    ...checks.map((item) => [
      item.timestamp,
      item.name,
      item.target || "",
      item.result,
      String(item.token_total || 0),
      String(Number(item.duration_seconds || 0).toFixed(2)),
    ]),
  ];
  const csv = `${lines.map((row) => row.map(csvEscape).join(",")).join("\n")}\n`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "rootcause-activity.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function renderCheckSettings(rules) {
  if (!checkSettingsTable) return;
  if (checkSettingsCount) checkSettingsCount.textContent = `${rules.length} check${rules.length === 1 ? "" : "s"}`;
  if (!rules.length) {
    checkSettingsTable.innerHTML = '<tr><td colspan="4" class="empty">No checks configured.</td></tr>';
    return;
  }
  checkSettingsTable.innerHTML = rules.map((rule) => {
    const enabled = rule.enabled !== false;
    return `<tr>
      <td><strong>${escapeHtml(rule.name)}</strong>${rule.description && rule.description !== rule.name ? `<br><small class="muted">${escapeHtml(rule.description)}</small>` : ""}</td>
      <td><small>${escapeHtml(rule.type || "check")}</small></td>
      <td><small>${escapeHtml(rule.schedule || "")}</small></td>
      <td style="text-align:center">
        <label class="toggle-label">
          <input type="checkbox" class="check-enabled-toggle" data-rule-id="${escapeAttr(rule.id || rule.name)}" ${enabled ? "checked" : ""}>
          <span class="toggle-track"></span>
        </label>
      </td>
    </tr>`;
  }).join("");
  checkSettingsTable.querySelectorAll(".check-enabled-toggle").forEach((checkbox) => {
    checkbox.addEventListener("change", async () => {
      const ruleId = checkbox.dataset.ruleId;
      const enabled = checkbox.checked;
      try {
        const response = await fetch("/api/alert/toggle-enabled", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: ruleId, enabled }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "failed");
        if (latestReport && data.alert_rules) latestReport.alert_rules = data.alert_rules;
      } catch (error) {
        checkbox.checked = !enabled;
        alert(`Failed to update check: ${error.message}`);
      }
    });
  });
}

async function loadAndRenderCheckSettings() {
  try {
    const response = await fetch("/api/config");
    if (!response.ok) return;
    const config = await response.json();
    renderCheckSettings(config.alert_rules || []);
  } catch (_) {
    // non-critical
  }
}

function buildAgentModelControl(agent, agentModels) {
  const agentType = agent.type || agent.name;
  const models = agentModels[agentType] || [];
  const currentModel = agent.model || "";
  if (!models.length) {
    return `<input type="text" class="agent-model-input" data-agent-name="${escapeAttr(agent.name)}" placeholder="default" value="${escapeAttr(currentModel)}">`;
  }
  const knownIds = new Set(models.map((m) => m.id));
  const customOption = currentModel && !knownIds.has(currentModel)
    ? `<option value="${escapeAttr(currentModel)}" selected>${escapeHtml(currentModel)} (custom)</option>`
    : "";
  const options = [
    `<option value="">default</option>`,
    ...models.map((m) => `<option value="${escapeAttr(m.id)}"${m.id === currentModel ? " selected" : ""}>${escapeHtml(m.name)}</option>`),
    customOption,
  ].join("");
  return `<select class="agent-model-input" data-agent-name="${escapeAttr(agent.name)}">${options}</select>`;
}

function renderAgentsSettings(config, agentModels = {}) {
  if (!config || !agentsModelGrid) return;
  const agents = config.agents || [];
  const cooldown = config.alerting?.agent_cooldown_minutes ?? 60;
  if (globalAgentCooldown) globalAgentCooldown.value = String(cooldown);
  agentsModelGrid.innerHTML = agents.length
    ? agents.map((agent) => `
      <label>
        <span>${escapeHtml(agent.name)} model</span>
        ${buildAgentModelControl(agent, agentModels)}
      </label>`).join("")
    : '<p class="caption">No agents configured in checks.json.</p>';
}

function renderAgentCallsLog(calls) {
  if (!agentCallsTable) return;
  agentCallsCount.textContent = `${calls.length} call${calls.length === 1 ? "" : "s"}`;
  if (!calls.length) {
    agentCallsTable.innerHTML = '<tr><td colspan="9" class="empty">No agent calls recorded yet.</td></tr>';
    return;
  }
  const rows = [...calls].reverse().slice(0, 200);
  agentCallsTable.innerHTML = rows.map((item) => {
    const ts = item.timestamp ? formatDateTime(item.timestamp) : "-";
    const resultClass = item.cooldown_skipped ? "maintenance" : item.success ? "fixed" : "fix_failed";
    const resultLabel = item.cooldown_skipped ? "cooldown" : item.success ? "ok" : "failed";
    const stageLabel = item.stage || (item.cooldown_skipped ? "—" : "fix");
    const stageClass = item.stage === "analysis" ? "sev-info" : item.stage === "eval" ? "sev-warn" : "";
    return `<tr>
      <td><small>${escapeHtml(ts)}</small></td>
      <td>${escapeHtml(item.check_name || "-")}</td>
      <td>${escapeHtml(item.target || "-")}</td>
      <td><span class="sev-pill ${stageClass}">${escapeHtml(stageLabel)}</span></td>
      <td>${escapeHtml(item.agent_name || (item.cooldown_skipped ? "—" : "-"))}</td>
      <td><small>${escapeHtml(item.model || "-")}</small></td>
      <td><small>${item.total_tokens > 0 ? item.total_tokens.toLocaleString() : "-"}</small></td>
      <td><small>${item.duration_seconds > 0 ? item.duration_seconds.toFixed(1) + "s" : "-"}</small></td>
      <td><span class="result-pill ${resultClass}">${resultLabel}</span></td>
    </tr>`;
  }).join("");
}

async function loadAndRenderAgentCalls() {
  try {
    const response = await fetch("/api/agent-calls");
    if (!response.ok) return;
    const calls = await response.json();
    renderAgentCallsLog(Array.isArray(calls) ? calls : []);
  } catch (_) {
    // non-critical
  }
}

async function loadAndRenderAgentsSettings() {
  try {
    const [configResp, modelsResp] = await Promise.all([fetch("/api/config"), fetch("/api/agent-models")]);
    if (!configResp.ok) return;
    const config = await configResp.json();
    const agentModels = modelsResp.ok ? await modelsResp.json() : {};
    renderAgentsSettings(config, agentModels);
    // Populate pipeline form
    const pipeline = config.ai_pipeline || {};
    if (pipelineEnabled) pipelineEnabled.checked = Boolean(pipeline.enabled);
    if (pipelineAnalysisModel) pipelineAnalysisModel.value = pipeline.analysis?.model || "";
    if (pipelineFixModel) pipelineFixModel.value = pipeline.fix?.model || "";
    if (pipelineSaveStatus) pipelineSaveStatus.textContent = pipeline.enabled ? "Enabled" : "Disabled";
  } catch (_) {
    // non-critical
  }
}

function renderSettingsView() {
  // Datasources don't depend on the mobile admin overview, so render them first.
  renderDatasourcesSettings(latestReport || {});
  renderWebhooksSettings(latestReport || {});
  const overview = mobileAdminOverview;
  if (!overview) {
    mobileSecurityStatus.textContent = "loading...";
    mobileEndpointSaveStatus.textContent = "loading...";
    maintenanceSaveStatus.textContent = "loading...";
    maintenanceTable.innerHTML = '<tr><td colspan="7" class="empty">Loading maintenance windows...</td></tr>';
    apiKeysTable.innerHTML = '<tr><td colspan="7" class="empty">Loading mobile settings...</td></tr>';
    mobileDevicesTable.innerHTML = '<tr><td colspan="6" class="empty">Loading devices...</td></tr>';
    return;
  }
  renderSettingsHosts();
  const hosts = Object.keys(latestReport?.host_catalog || {}).sort((a, b) => a.localeCompare(b));
  const alerts = [...(latestReport?.alert_rules || [])].sort((a, b) => a.name.localeCompare(b.name));
  maintenanceHost.innerHTML = `<option value="">Select host</option>${hosts.map((host) => `<option value="${escapeAttr(host)}">${escapeHtml(host)}</option>`).join("")}`;
  maintenanceAlert.innerHTML = `<option value="">Select alert</option>${alerts.map((alert) => `<option value="${escapeAttr(alert.id || alert.name)}">${escapeHtml(alert.name)}</option>`).join("")}`;
  const windows = latestReport?.maintenance_windows || [];
  maintenanceCount.textContent = `${windows.length} window${windows.length === 1 ? "" : "s"}`;
  maintenanceTable.innerHTML = windows.length ? windows.map((item) => `
    <tr>
      <td>${escapeHtml(item.scope)}</td>
      <td>${escapeHtml(item.scope === "host" ? item.host : `${item.alert_name || item.alert_id}${item.host ? ` · ${item.host}` : ""}`)}</td>
      <td>${escapeHtml(formatDateTime(item.starts_at))}</td>
      <td>${escapeHtml(formatDateTime(item.ends_at))}</td>
      <td>${escapeHtml(item.reason || "-")}</td>
      <td><span class="result-pill ${item.active ? "fixed" : "pass"}">${item.active ? "active" : "scheduled"}</span></td>
      <td><button class="danger-button maintenance-delete-button" type="button" data-window-id="${escapeAttr(item.id)}">Delete</button></td>
    </tr>
  `).join("") : '<tr><td colspan="7" class="empty">No maintenance windows scheduled.</td></tr>';
  maintenanceTable.querySelectorAll(".maintenance-delete-button").forEach((node) => {
    node.addEventListener("click", async () => {
      try {
        const response = await fetch("/api/maintenance/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: node.dataset.windowId }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "failed to delete");
        maintenanceSaveStatus.textContent = "Deleted";
        await loadStatus(true);
      } catch (error) {
        maintenanceSaveStatus.textContent = error.message;
      }
    });
  });
  mobileSecurityStatus.textContent = overview.mobile?.require_https ? "HTTPS enforced" : "HTTPS disabled";
  mobileEndpointSaveStatus.textContent = overview.mobile?.public_base_url || "No public endpoint configured";
  mobilePublicEndpointLabel.textContent = overview.mobile?.public_base_url || "not configured";
  mobilePublicScheme.value = overview.mobile?.public_scheme || "https";
  mobilePublicHostname.value = overview.mobile?.public_hostname || "";
  mobilePublicPort.value = String(overview.mobile?.public_port || 443);
  mobileServeHost.value = overview.ui?.serve_host || "127.0.0.1";
  mobileServePort.value = String(overview.ui?.serve_port || 8787);
  mobileTlsEnabled.checked = Boolean(overview.ui?.tls_enabled);
  mobileTlsCertfile.value = overview.ui?.tls_certfile || "";
  mobileTlsKeyfile.value = overview.ui?.tls_keyfile || "";
  if (mobileApkDownloadLink) {
    const apkPath = overview.downloads?.apk_path || "/downloads/rootcause.apk";
    const apkAvailable = Boolean(overview.downloads?.apk_available);
    mobileApkDownloadLink.href = apkPath;
    mobileApkDownloadLink.setAttribute("aria-disabled", apkAvailable ? "false" : "true");
    if (apkAvailable) {
      mobileApkDownloadLink.removeAttribute("tabindex");
      mobileApkDownloadLink.style.pointerEvents = "";
      mobileApkDownloadLink.style.opacity = "";
      mobileApkDownloadNote.textContent = "Served directly by RootCause from the current release build.";
    } else {
      mobileApkDownloadLink.setAttribute("tabindex", "-1");
      mobileApkDownloadLink.style.pointerEvents = "none";
      mobileApkDownloadLink.style.opacity = "0.55";
      mobileApkDownloadNote.textContent = "No release APK found yet. Build it first from android/build-release.sh.";
    }
  }
  const pushConfig = overview.push || {};
  if (fcmForm) {
    document.querySelector("#fcm-enabled").checked = Boolean(pushConfig.enabled);
    document.querySelector("#fcm-service-account-path").value = pushConfig.service_account_path || "";
    fcmSaveStatus.textContent = pushConfig.enabled ? "Enabled" : "Disabled";
  }
  const apiKeys = overview.api_keys || [];
  const devices = overview.devices || [];
  apiKeysCount.textContent = `${apiKeys.length} keys`;
  mobileDevicesCount.textContent = `${devices.length} devices`;
  apiKeysTable.innerHTML = apiKeys.length ? apiKeys.map((item) => `
    <tr>
      <td>${escapeHtml(item.name)}</td>
      <td><code>${escapeHtml(item.key_prefix || "-")}</code></td>
      <td>${escapeHtml((item.allowed_targets || []).join(", ") || "all")}</td>
      <td>${escapeHtml((item.scopes || []).join(", "))}</td>
      <td>${escapeHtml(`${item.device_count}/${item.device_limit}`)}</td>
      <td>${escapeHtml(item.last_used_at ? formatDateTime(item.last_used_at) : "never")}</td>
      <td><button class="danger-button mobile-revoke-key" type="button" data-key-id="${escapeAttr(item.id)}">Revoke</button></td>
    </tr>
  `).join("") : '<tr><td colspan="7" class="empty">No API keys yet.</td></tr>';
  mobileDevicesTable.innerHTML = devices.length ? devices.map((item) => `
    <tr>
      <td>${escapeHtml(item.name || item.id)}</td>
      <td>${escapeHtml(`${item.platform || "-"} ${item.model || ""}`.trim())}</td>
      <td>${escapeHtml(item.api_key_id || "-")}</td>
      <td>${escapeHtml(item.last_seen_at ? formatDateTime(item.last_seen_at) : "never")}</td>
      <td>${escapeHtml(`${item.host || "-"}:${item.port || "-"}`)}</td>
      <td><button class="danger-button mobile-revoke-device" type="button" data-device-id="${escapeAttr(item.id)}">Revoke</button></td>
    </tr>
  `).join("") : '<tr><td colspan="6" class="empty">No mobile devices registered yet.</td></tr>';
  apiKeysTable.querySelectorAll(".mobile-revoke-key").forEach((node) => {
    node.addEventListener("click", async () => {
      try { await revokeApiKey(node.dataset.keyId); } catch (err) { alert(err.message); }
    });
  });
  mobileDevicesTable.querySelectorAll(".mobile-revoke-device").forEach((node) => {
    node.addEventListener("click", async () => {
      try { await revokeMobileDevice(node.dataset.deviceId); } catch (err) { alert(err.message); }
    });
  });
  loadAndRenderAgentsSettings();
  loadAndRenderAgentCalls();
  loadAndRenderCheckSettings();
}

function getNotifications(report) {
  const alerts = getAlertGroups(report);
  const active = alerts.filter((item) => item.realState !== "ok").map((item) => ({
    alertId: item.id,
    alertName: item.name,
    title: item.name,
    body: item.latestDetail || item.subtitle,
    meta: item.statusText,
    actionable: true,
  }));
  const history = (report.history?.checks || [])
    .filter((item) => item.result !== "pass")
    .slice(-6)
    .reverse()
    .map((item) => ({
      title: `${item.name} · ${item.result}`,
      body: item.detail || item.target || "-",
      meta: formatDateTime(item.timestamp),
      alertId: Object.fromEntries((report.alert_rules || []).map((rule) => [rule.name, rule.id]))[item.name] || "",
      alertName: item.name,
    }));
  return [...active, ...history].slice(0, 10);
}

function renderNotifications(report) {
  const items = getNotifications(report);
  notificationsButton.dataset.count = String(items.length);
  notificationsPopup.innerHTML = items.length ? items.map((item) => `
    <div class="notification-item" ${item.alertId ? `data-alert-id="${escapeAttr(item.alertId)}"` : ""}>
      <strong>${escapeHtml(item.title)}</strong>
      <p>${escapeHtml(item.body)}</p>
      <small>${escapeHtml(item.meta)}</small>
      ${item.actionable ? renderQuickActionGroup({ id: item.alertId, name: item.alertName }) : ""}
    </div>
  `).join("") : '<div class="empty">No notifications.</div>';
  notificationsPopup.classList.toggle("is-open", notificationsOpen);
  notificationsPopup.querySelectorAll(".notification-item[data-alert-id]").forEach((node) => {
    node.addEventListener("click", () => {
      if (node.dataset.ignoreRowClick === "true") return;
      selectedAlertId = node.dataset.alertId;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
  attachQuickActionHandlers(notificationsPopup, report);
}

function renderAlertList(report) {
  // Orchestrator mode (native engine off): the sidebar is problem-centric, not
  // check-centric — checks no longer drive the left rail.
  if (report.native_engine_enabled === false) {
    renderSidebarProblems();
    return;
  }
  const query = alertSearch.value.trim().toLowerCase();
  const groupedAlerts = getAlertGroups(report);
  const alerts = groupedAlerts.filter((item) => {
    if (sidebarStateFilter !== "all" && item.realState !== sidebarStateFilter) return false;
    if (!query) return true;
    return `${item.name} ${item.description} ${item.latestDetail} ${item.targets.join(" ")}`.toLowerCase().includes(query);
  });

  const counts = groupedAlerts.reduce((acc, item) => {
    if (item.realState === "failing") acc.failing += 1;
    else if (item.realState === "idle") acc.idle += 1;
    else acc.ok += 1;
    return acc;
  }, { ok: 0, failing: 0, idle: 0 });
  sidebarOverview.innerHTML = `
    <button class="overview-pill bad ${sidebarStateFilter === "failing" ? "is-active" : ""}" data-filter="failing" type="button">${counts.failing} failing</button>
    <button class="overview-pill warn ${sidebarStateFilter === "idle" ? "is-active" : ""}" data-filter="idle" type="button">${counts.idle} idle</button>
    <button class="overview-pill ok ${sidebarStateFilter === "ok" ? "is-active" : ""}" data-filter="ok" type="button">${counts.ok} ok</button>
  `;
  sidebarOverview.querySelectorAll("[data-filter]").forEach((node) => {
    node.addEventListener("click", () => {
      const next = node.dataset.filter;
      sidebarStateFilter = sidebarStateFilter === next ? "all" : next;
      renderAlertList(report);
    });
  });

  if (!alerts.length) {
    alertList.innerHTML = '<div class="empty">No alerts match the current filter.</div>';
    return;
  }

  alertList.innerHTML = "";
  alerts.forEach((item) => {
    const node = alertTemplate.content.firstElementChild.cloneNode(true);
    node.classList.toggle("is-active", item.id === selectedAlertId && activePage === "alert");
    node.querySelector(".alert-item-name").textContent = item.name;
    if (item.config?.locked) {
      node.querySelector(".alert-item-name").insertAdjacentHTML("afterbegin", '<span class="lock-badge" title="Bloqueado">🔒</span> ');
    }
    node.querySelector(".alert-item-meta").innerHTML = `
      <span>${escapeHtml(item.subtitle)}</span>
      <span>${escapeHtml(item.targets.join(", "))}</span>
      <span>${escapeHtml(item.latestAgent ? `agent ${item.latestAgent}` : item.realState === "idle" ? "waiting rearm" : "no active agent")}</span>
      <span>${escapeHtml(item.consecutiveFailures ? `${item.consecutiveFailures} consecutive failures` : "healthy")}</span>
    `;
    const status = node.querySelector(".alert-item-status");
    status.className = `alert-item-status ${item.statusClass}`;
    status.textContent = iconForAlert(item);
    node.addEventListener("click", () => {
      selectedAlertId = item.id;
      activePage = "alert";
      notificationsOpen = false;
      syncRoute();
      render(report);
    });
    alertList.appendChild(node);
  });
}

function renderSummary(report, alert, entries) {
  const successfulRuns = entries.filter((e) => e.success).length;
  const avgDuration = entries.length
    ? (entries.reduce((sum, e) => sum + (e.duration_seconds || 0), 0) / entries.length).toFixed(2)
    : report.duration_seconds.toFixed(2);
  const successRate = entries.length ? ((successfulRuns / entries.length) * 100).toFixed(1) : "100.0";

  const failingChecks = alert.checks.filter((c) => !["pass", "fixed"].includes(c.result));
  const latestCheck = failingChecks[0] || alert.checks[0];
  const paused = Boolean(latestCheck?.alert_state?.schedule_paused);
  const isBad = alert.statusClass === "bad";

  const statusTitle = paused ? "Paused after failed remediation"
    : isBad ? "Action needed"
    : alert.fixedCount ? "Recovered"
    : "Operational";

  const detailText = paused
    ? (latestCheck?.alert_state?.schedule_pause_reason || "Auto-paused after unresolved remediation failure")
    : latestCheck?.detail || alert.description || "";

  const metaParts = [];
  const consecFails = latestCheck?.alert_state?.consecutive_failures;
  if (consecFails > 1) metaParts.push(`${consecFails} consecutive failures`);
  if (paused && latestCheck?.alert_state?.schedule_paused_at) {
    metaParts.push(`Paused ${formatRelativeTime(latestCheck.alert_state.schedule_paused_at)}`);
  }
  const metaHtml = metaParts.length ? `<p class="status-meta">${escapeHtml(metaParts.join(" · "))}</p>` : "";

  const alertState = latestCheck?.alert_state || {};
  // When paused, live agent_attempts are usually empty (the result is rebuilt
  // from cache), so fall back to the forensic snapshot captured at pause time.
  const pauseAttempts = Array.isArray(alertState.pause_attempts) ? alertState.pause_attempts : [];
  const liveAttempts = latestCheck?.agent_attempts || [];
  const attempts = (paused && pauseAttempts.length) ? pauseAttempts : liveAttempts;
  const attemptsHtml = attempts.length ? `
    <div class="status-attempts">
      <p class="status-section-label">${paused && pauseAttempts.length ? "Remediation attempts before pause" : "Remediation attempts"}</p>
      ${attempts.map((a) => `
        <div class="attempt-row ${a.success ? "success" : "failed"}">
          <div class="attempt-row-head">
            <span class="attempt-agent">${escapeHtml(a.agent || "agent")}</span>
            <span class="result-pill ${a.success ? "fixed" : "bad"}">${a.success ? "fixed" : "failed"}</span>
            ${a.stage ? `<span class="caption">${escapeHtml(a.stage)}</span>` : ""}
            ${a.estimated_tokens ? `<span class="caption">${a.estimated_tokens.toLocaleString()} tokens</span>` : ""}
          </div>
          ${a.output ? `<pre class="attempt-output">${escapeHtml(a.output)}</pre>` : ""}
        </div>
      `).join("")}
    </div>
  ` : "";

  // Forensic block: what actually went wrong the last time this check failed and
  // got auto-paused. Surfaced so a paused check isn't just a blank "paused".
  let pauseInfoHtml = "";
  if (paused) {
    const failureDetail = alertState.pause_failure_detail || latestCheck?.detail || "";
    const lastOutput = alertState.pause_last_output || "";
    const consec = alertState.pause_consecutive_failures || alertState.consecutive_failures;
    const pausedAt = alertState.schedule_paused_at;
    const rows = [];
    if (pausedAt) rows.push(`<div class="pause-fact"><span>Paused at</span><strong>${escapeHtml(formatDateTime(pausedAt))} (${escapeHtml(formatRelativeTime(pausedAt))})</strong></div>`);
    if (consec) rows.push(`<div class="pause-fact"><span>Consecutive failures</span><strong>${escapeHtml(String(consec))}</strong></div>`);
    const factsHtml = rows.length ? `<div class="pause-facts">${rows.join("")}</div>` : "";
    const failureHtml = failureDetail ? `<p class="status-section-label">Failing condition at pause</p><pre class="status-detail-text">${escapeHtml(failureDetail)}</pre>` : "";
    const outputHtml = (lastOutput && lastOutput !== failureDetail) ? `<p class="status-section-label">Last remediation output</p><pre class="attempt-output">${escapeHtml(lastOutput)}</pre>` : "";
    if (factsHtml || failureHtml || outputHtml) {
      pauseInfoHtml = `<div class="pause-info-block">${factsHtml}${failureHtml}${outputHtml}</div>`;
    }
  }

  const aId = escapeAttr(alert.id || "");
  const aName = escapeAttr(alert.name);
  const actionsHtml = `
    <div class="status-actions">
      <button class="secondary-button status-action" data-action="rerun" data-alert-id="${aId}" data-alert-name="${aName}" type="button">Re-Run</button>
      ${paused ? `<button class="secondary-button status-action" data-action="rearm" data-alert-id="${aId}" data-alert-name="${aName}" type="button">Rearm</button>` : ""}
      ${isBad || paused ? `<button class="secondary-button status-action" data-action="ack" data-alert-id="${aId}" data-alert-name="${aName}" type="button">Acknowledge</button>` : ""}
      ${isBad || paused ? `<button class="secondary-button status-action" data-action="silence" data-alert-id="${aId}" data-alert-name="${aName}" type="button">Silence 1h</button>` : ""}
    </div>
  `;

  const detailBlockHtml = detailText && (isBad || paused) ? `
    <div class="status-detail-block">
      <pre class="status-detail-text">${escapeHtml(detailText)}</pre>
    </div>
  ` : "";

  summaryCards.innerHTML = `
    <article class="panel stat-card status-panel">
      <label>Current Status</label>
      <div class="status-panel-head">
        <span class="status-badge ${alert.statusClass}">${iconForAlert({ statusClass: alert.statusClass })}</span>
        <div class="status-panel-copy">
          <strong>${escapeHtml(statusTitle)}</strong>
          ${metaHtml}
        </div>
        ${actionsHtml}
      </div>
      ${detailBlockHtml}
      ${pauseInfoHtml}
      ${attemptsHtml}
    </article>
  `;

  summaryCards.querySelectorAll(".status-action").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const action = btn.dataset.action;
      btn.disabled = true;
      try {
        if (action === "rearm") {
          await rearmAlert();
        } else {
          await runQuickAlertAction(action, btn.dataset.alertId, btn.dataset.alertName);
        }
      } catch (err) {
        showToast(`${action} failed: ${err.message}`, "error");
      } finally {
        btn.disabled = false;
      }
    });
  });

  const runMetricsPanel = document.querySelector("#run-metrics-panel");
  if (runMetricsPanel) {
    runMetricsPanel.innerHTML = `
      <label>Run Metrics</label>
      <div class="compact-metrics">
        <div class="compact-metric">
          <strong>${formatRelativeTime(report.timestamp)}</strong>
          <span>Last run</span>
        </div>
        <div class="compact-metric">
          <strong>${successRate}%</strong>
          <span>Success rate</span>
        </div>
        <div class="compact-metric">
          <strong>${avgDuration}s</strong>
          <span>Avg duration</span>
        </div>
      </div>
      <p>${formatDateTime(report.timestamp)}</p>
    `;
  }
}

function renderExecutions(alert, entries) {
  const rows = entries.slice(0, 8);
  executionsTitle.textContent = `${alert.name} activity`;
  executionCount.textContent = `${entries.length} runs`;

  if (!rows.length) {
    executionsTable.innerHTML = '<tr><td colspan="4" class="empty">No execution history yet.</td></tr>';
    return;
  }

  executionsTable.innerHTML = rows.map((item) => `
    <tr>
      <td>${formatDateTime(item.timestamp)}</td>
      <td><span class="result-pill ${item.result}">${resultLabel(item.result)}</span></td>
      <td>${(item.duration_seconds || 0).toFixed(2)}s</td>
      <td>${item.target}</td>
    </tr>
  `).join("");
}

function renderHostsPreview(alert, report) {
  const rows = (alert?.targets || []).map((hostName) => {
    const host = report.host_catalog?.[hostName] || {};
    return {
      name: hostName,
      ip: host.address || "-",
      user: host.ssh_user || "local",
      type: host.connection || "-",
    };
  });

  hostsPreviewCount.textContent = String(rows.length);
  if (!rows.length) {
    hostsPreview.innerHTML = '<div class="empty">No hosts assigned.</div>';
    return;
  }
  hostsPreview.innerHTML = rows.map((row) => `
    <div class="mini-table-row">
      <div>
        <strong>${escapeHtml(row.name)}</strong>
        <small>${escapeHtml(row.ip)}</small>
      </div>
      <div>
        <span>${escapeHtml(row.user)}</span><br>
        <small>${escapeHtml(row.type)}</small>
      </div>
    </div>
  `).join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function getExternalAlerts(report) {
  return [...(report.external_alerts || [])].sort((a, b) => {
    const stateRank = { active: 0, firing: 0, pending: 1, suppressed: 2, unprocessed: 3 };
    const rankA = stateRank[a.state] ?? 9;
    const rankB = stateRank[b.state] ?? 9;
    return rankA - rankB || String(a.host || "").localeCompare(String(b.host || "")) || String(a.name || "").localeCompare(String(b.name || ""));
  });
}

function externalAlertStateClass(alert) {
  if (alert.silenced) return "fix_failed";
  if (["active", "firing"].includes(alert.state)) return "failed";
  return "pass";
}

function renderHostsEditor(report) {
  const entries = Object.entries(report.host_catalog || {});
  hostsCount.textContent = `${entries.length} host${entries.length === 1 ? "" : "s"}`;

  if (!entries.length) {
    hostsEditTable.innerHTML = '<tr><td colspan="13" class="empty">No hosts configured. Click Add Host.</td></tr>';
    return;
  }

  hostsEditTable.innerHTML = entries.map(([name, host]) => `
    <tr data-original-name="${escapeAttr(name)}">
      <td><input type="text" class="host-input" data-field="name" value="${escapeAttr(name)}"></td>
      <td><input type="text" class="host-input" data-field="address" value="${escapeAttr(host.address || "")}"></td>
      <td><input type="text" class="host-input" data-field="ssh_user" value="${escapeAttr(host.ssh_user || "")}"></td>
      <td><input type="number" class="host-input" data-field="ssh_port" min="1" step="1" value="${escapeAttr(host.ssh_port || 22)}"></td>
      <td><input type="text" class="host-input" data-field="ssh_key_path" value="${escapeAttr(host.ssh_key_path || "")}" placeholder="~/.ssh/id_ed25519"></td>
      <td>
        <select class="host-input" data-field="connection">
          <option value="ssh"${host.connection === "ssh" ? " selected" : ""}>ssh</option>
          <option value="local"${host.connection === "local" ? " selected" : ""}>local</option>
        </select>
      </td>
      <td><input type="text" class="host-input" data-field="workdir" value="${escapeAttr(host.workdir || "")}" placeholder="/srv/app"></td>
      <td><input type="text" class="host-input" data-field="prometheus_url" value="${escapeAttr(host.prometheus_url || "")}"></td>
      <td><input type="text" class="host-input" data-field="alertmanager_url" value="${escapeAttr(host.alertmanager_url || "")}"></td>
      <td><input type="text" class="host-input" data-field="grafana_url" value="${escapeAttr(host.grafana_url || "")}" placeholder="http://host:3001"></td>
      <td><input type="text" class="host-input" data-field="pushgateway_url" value="${escapeAttr(host.pushgateway_url || "")}"></td>
      <td><input type="text" class="host-input" data-field="role" value="${escapeAttr(host.labels?.role || "")}"></td>
      <td><input type="checkbox" class="host-input" data-field="enabled"${host.enabled !== false ? " checked" : ""}></td>
      <td class="host-actions">
        <button class="danger-button host-delete-button" type="button">Delete</button>
      </td>
    </tr>
  `).join("");

  hostsEditTable.querySelectorAll("tr[data-original-name]").forEach((row) => {
    row.querySelector(".host-delete-button").addEventListener("click", () => deleteHostRow(row));
    attachHostAutosave(row);
  });
}

function readHostRow(row) {
  // Only collect fields whose inputs exist in this row, so both the full
  // Targets-tab table and the focused Settings → Hosts editor can share this.
  const payload = { original_name: row.dataset.originalName || "" };
  const textFields = [
    "name", "alias", "address", "ssh_user", "ssh_key_path", "workdir",
    "prometheus_url", "prometheus_instance", "alertmanager_url", "grafana_url",
    "pushgateway_url", "role",
  ];
  textFields.forEach((f) => {
    const el = row.querySelector(`[data-field="${f}"]`);
    if (el) payload[f] = el.value.trim();
  });
  const portEl = row.querySelector('[data-field="ssh_port"]');
  if (portEl) payload.ssh_port = Number(portEl.value || 22);
  const connEl = row.querySelector('[data-field="connection"]');
  if (connEl) payload.connection = connEl.value;
  const enabledEl = row.querySelector('[data-field="enabled"]');
  if (enabledEl) payload.enabled = enabledEl.checked;
  return payload;
}

function markHostRowState(row, message, tone = "idle") {
  row.dataset.saveState = tone;
  row.title = message;
}

function hostRowMinimumValid(row) {
  const payload = readHostRow(row);
  return Boolean(payload.name && (payload.connection === "local" || payload.address));
}

function attachHostAutosave(row) {
  row.querySelectorAll(".host-input").forEach((input) => {
    const eventName = input.type === "checkbox" || input.tagName === "SELECT" ? "change" : "input";
    input.addEventListener(eventName, () => scheduleHostAutosave(row));
    if (eventName !== "change") {
      input.addEventListener("change", () => scheduleHostAutosave(row));
    }
  });
}

function scheduleHostAutosave(row) {
  const key = row.dataset.originalName || `new:${row.rowIndex}`;
  hostFormDirty = true;
  clearTimeout(hostAutosaveTimers.get(key));
  hostAutosaveTimers.delete(key);
  if (!hostRowMinimumValid(row)) {
    markHostRowState(row, "Host draft incomplete");
    return;
  }
  markHostRowState(row, "Saving host...", "saving");
  const timer = setTimeout(() => {
    hostAutosaveTimers.delete(key);
    void saveHostRow(row);
  }, 500);
  hostAutosaveTimers.set(key, timer);
}

async function saveHostRow(row) {
  const payload = readHostRow(row);
  const key = row.dataset.originalName || `new:${row.rowIndex}`;
  if (!payload.name || (payload.connection !== "local" && !payload.address)) {
    markHostRowState(row, "Host draft incomplete");
    return;
  }
  try {
    const response = await fetch("/api/host", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to save host");
    hostAutosaveTimers.delete(key);
    markHostRowState(row, "Host saved", "saved");
    hostFormDirty = false;
    await loadStatus(true);
  } catch (error) {
    markHostRowState(row, `Host save failed: ${error.message}`, "error");
  }
}

async function deleteHostRow(row) {
  const name = row.dataset.originalName;
  if (!name) {
    row.remove();
    return;
  }
  if (!confirm(`Delete host "${name}"? It will be removed from any alert targeting it.`)) return;
  try {
    const response = await fetch("/api/host/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to delete host");
    await loadStatus();
  } catch (error) {
    alert(`Delete host failed: ${error.message}`);
  }
}

function addHostRow() {
  const empty = document.createElement("tr");
  empty.dataset.originalName = "";
  empty.innerHTML = `
    <td><input type="text" class="host-input" data-field="name" placeholder="my-host"></td>
    <td><input type="text" class="host-input" data-field="address" placeholder="192.168.1.10"></td>
    <td><input type="text" class="host-input" data-field="ssh_user" value="ivan"></td>
    <td><input type="number" class="host-input" data-field="ssh_port" min="1" step="1" value="22"></td>
    <td><input type="text" class="host-input" data-field="ssh_key_path" placeholder="~/.ssh/id_ed25519"></td>
    <td>
      <select class="host-input" data-field="connection">
        <option value="ssh" selected>ssh</option>
        <option value="local">local</option>
      </select>
    </td>
    <td><input type="text" class="host-input" data-field="workdir" placeholder="/srv/app"></td>
    <td><input type="text" class="host-input" data-field="prometheus_url" placeholder="http://host:9090"></td>
    <td><input type="text" class="host-input" data-field="alertmanager_url" placeholder="http://host:9093"></td>
    <td><input type="text" class="host-input" data-field="pushgateway_url" placeholder="http://host:9091"></td>
    <td><input type="text" class="host-input" data-field="role" placeholder="server"></td>
    <td><input type="checkbox" class="host-input" data-field="enabled" checked></td>
    <td class="host-actions">
      <button class="danger-button host-delete-button" type="button">Cancel</button>
    </td>
  `;
  if (hostsEditTable.querySelector(".empty")) hostsEditTable.innerHTML = "";
  hostsEditTable.prepend(empty);
  empty.querySelector(".host-delete-button").addEventListener("click", () => empty.remove());
  attachHostAutosave(empty);
}

// Focused host + alias manager in Settings → Hosts (shares the host autosave/save).
function settingsHostRowHtml(name, host) {
  return `<tr data-original-name="${escapeAttr(name)}">
    <td><input type="text" class="host-input" data-field="name" value="${escapeAttr(name)}"></td>
    <td><input type="text" class="host-input" data-field="alias" value="${escapeAttr(host.alias || "")}" placeholder="${escapeAttr(name)}"></td>
    <td><input type="text" class="host-input" data-field="address" value="${escapeAttr(host.address || "")}"></td>
    <td><select class="host-input" data-field="connection"><option value="ssh"${host.connection === "ssh" ? " selected" : ""}>ssh</option><option value="local"${host.connection === "local" ? " selected" : ""}>local</option></select></td>
    <td><input type="text" class="host-input" data-field="prometheus_url" value="${escapeAttr(host.prometheus_url || "")}" placeholder="http://host:9090"></td>
    <td><input type="text" class="host-input" data-field="prometheus_instance" value="${escapeAttr(host.prometheus_instance || "")}" placeholder="localhost"></td>
    <td><input type="text" class="host-input" data-field="grafana_url" value="${escapeAttr(host.grafana_url || "")}" placeholder="http://host:3001"></td>
    <td><input type="checkbox" class="host-input" data-field="enabled"${host.enabled !== false ? " checked" : ""}></td>
    <td class="host-actions"><button class="danger-button host-delete-button" type="button">Delete</button></td>
  </tr>`;
}

function renderSettingsHosts() {
  const tbody = document.querySelector("#settings-hosts-table");
  if (!tbody) return;
  const entries = Object.entries((latestReport && latestReport.host_catalog) || {});
  const countEl = document.querySelector("#settings-hosts-count");
  if (countEl) countEl.textContent = `${entries.length} host${entries.length === 1 ? "" : "s"}`;
  if (!entries.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty">No hosts. Click Add Host.</td></tr>';
    return;
  }
  tbody.innerHTML = entries.map(([name, host]) => settingsHostRowHtml(name, host)).join("");
  tbody.querySelectorAll("tr[data-original-name]").forEach((row) => {
    row.querySelector(".host-delete-button").addEventListener("click", () => deleteHostRow(row));
    attachHostAutosave(row);
  });
}

function addSettingsHostRow() {
  const tbody = document.querySelector("#settings-hosts-table");
  if (!tbody) return;
  if (tbody.querySelector(".empty")) tbody.innerHTML = "";
  const tr = document.createElement("tr");
  tr.dataset.originalName = "";
  tr.innerHTML = settingsHostRowHtml("", {});
  tr.querySelector('[data-field="name"]').placeholder = "my-host";
  tr.querySelector('[data-field="address"]').placeholder = "192.168.1.10";
  tbody.prepend(tr);
  const del = tr.querySelector(".host-delete-button");
  del.textContent = "Cancel";
  del.addEventListener("click", () => tr.remove());
  attachHostAutosave(tr);
}

function setAgentCheckboxes(config) {
  const allowed = new Set(config.allowed_agents || []);
  const customAgent = (config.custom_agents || [])[0] || null;
  document.querySelector("#agent-claude").checked = allowed.has("claude");
  document.querySelector("#agent-codex").checked = allowed.has("codex");
  document.querySelector("#agent-opencode").checked = allowed.has("opencode");
  document.querySelector("#agent-custom-enabled").checked = Boolean(customAgent);
  document.querySelector("#custom-agent-name").value = customAgent?.name || "custom-run";
  document.querySelector("#custom-agent-command").value = customAgent?.command_template || "";
  document.querySelector("#custom-agent-fields").style.display = customAgent ? "grid" : "none";
}

// Only the fields each trigger type actually needs. Everything else is hidden
// so the editor stays minimal/operational per type.
const TRIGGER_FIELDS_BY_TYPE = {
  // ssh/local: just the command + a single "how to evaluate the output" selector.
  // Numeric (threshold/comparator) and certificate fields are intentionally not
  // shown here — checks that still use them (disk_root, ssl_certificates) keep
  // those values untouched (they round-trip through the hidden inputs).
  ssh: ["command", "ssh-eval", "ssh-match-text"],
  local: ["command", "ssh-eval", "ssh-match-text"],
  http: ["url", "http-expect"],
  prometheus_query: ["query", "prom-preview"],
  prometheus_targets: ["ignore-targets"],
  composite: ["steps"],
  network_ping: ["ping-targets"],
  alertmanager: ["alertmanager"],
};
const TRIGGER_ALL_FIELDS = [
  "command", "ssh-eval", "ssh-match-text", "url", "http-expect", "query", "prom-preview",
  "expect-empty", "expect-nonempty", "comparator", "threshold", "threshold-query",
  "accept-codes", "parse-cert-days", "cert-warn-days", "ignore-targets", "steps",
  "ping-targets", "alertmanager",
];

function triggerFieldEl(token) {
  const special = {
    "ping-targets": "#ping-targets-field",
    "alertmanager": "#alertmanager-type-fields",
    "http-expect": "#http-expect-field",
    "prom-preview": "#prom-preview",
    "ssh-eval": "#ssh-eval-field",
    "ssh-match-text": "#ssh-match-text-field",
  };
  if (special[token]) return document.querySelector(special[token]);
  const input = document.querySelector("#edit-" + token);
  return input ? input.closest("label") : null;
}

// The output-match text field only applies to the contains / not-contains modes.
function updateSshEvalVisibility() {
  const mode = document.querySelector("#edit-ssh-eval")?.value;
  const field = document.querySelector("#ssh-match-text-field");
  if (!field) return;
  const show = mode === "contains" || mode === "not_contains";
  if (show) field.style.removeProperty("display");
  else field.style.setProperty("display", "none", "important");
}

function updateTypeSpecificFields(type) {
  const show = new Set(TRIGGER_FIELDS_BY_TYPE[type] || ["command"]);
  TRIGGER_ALL_FIELDS.forEach((token) => {
    const el = triggerFieldEl(token);
    if (!el) return;
    if (show.has(token)) el.style.removeProperty("display");
    else el.style.setProperty("display", "none", "important"); // beats .editor-checkbox !important
  });
  if (type === "ssh" || type === "local") updateSshEvalVisibility();
  if (type === "prometheus_query") {
    wirePromPreview();
    renderPromHosts();
    refreshPromPreview();
  }
}

// ── Live PromQL preview chart (helps pick the exact query + threshold) ──────
let promPreviewWired = false;
let promPreviewTimer = null;
let promInstances = [];
const PROMQL_KEYWORDS = new Set([
  "by", "without", "on", "ignoring", "group_left", "group_right", "and", "or", "unless",
  "offset", "bool", "inf", "nan",
  // aggregation operators (followed by "(" or "by(")
  "sum", "avg", "min", "max", "count", "group", "stddev", "stdvar", "topk", "bottomk", "quantile", "count_values",
]);

// Strip any existing instance matcher and (optionally) append a new one.
function setInstanceMatcher(labels, matcher) {
  const parts = String(labels || "").split(",").map((s) => s.trim()).filter(Boolean)
    .filter((p) => !/^instance\s*(=~|!~|!=|=)/.test(p));
  if (matcher) parts.push(matcher);
  return parts.join(", ");
}

// Inject {instance=...} into every metric selector, leaving functions/keywords
// and the threshold comparison untouched — auto-builds PromQL for non-experts.
function applyInstanceToQuery(query, matcher) {
  const { metric, op, threshold } = parsePromExpr(query);
  const rest = op ? ` ${op} ${threshold}` : "";
  const newMetric = metric.replace(/([a-zA-Z_:][a-zA-Z0-9_:]*)(\s*\{([^}]*)\})?/g, (full, name, _braces, labels, offset, str) => {
    const prev = offset > 0 ? str[offset - 1] : "";
    if (/[0-9a-zA-Z_:]/.test(prev)) return full;        // mid-token / duration unit (e.g. 5m in [5m])
    if (str[offset + full.length] === "(") return full; // function call
    if (PROMQL_KEYWORDS.has(name)) return full;
    if (name === "instance") return full;               // label name in a by()/on() clause
    const lbl = setInstanceMatcher(labels || "", matcher);
    return lbl ? `${name}{${lbl}}` : name;
  });
  return newMetric + rest;
}

function currentInstanceSelection(query) {
  const m = String(query || "").match(/instance\s*(=~|=)\s*"([^"]*)"/);
  if (!m) return { mode: "none", set: new Set() };
  if (m[1] === "=") return { mode: "one", set: new Set([m[2]]) };
  if (m[2] === ".*") return { mode: "all", set: new Set() };
  return { mode: "multi", set: new Set(m[2].split("|")) };
}

function instanceMatcherFor(set, all) {
  if (all) return 'instance=~".*"';
  const arr = [...set].filter(Boolean);
  if (arr.length === 0) return "";
  if (arr.length === 1) return `instance="${arr[0]}"`;
  return `instance=~"${arr.join("|")}"`;
}

function setPromQuery(newQuery) {
  const el = document.querySelector("#edit-query");
  if (!el) return;
  if (el.value !== newQuery) {
    el.value = newQuery;
    markFieldPending(el);
    scheduleAlertAutosave();
  }
  refreshPromPreview();
}

function renderPromHosts() {
  const box = document.querySelector("#prom-hosts");
  if (!box) return;
  // Chips come from the RootCause host config (alias → prometheus_instance), so
  // they are stable and consistent regardless of which Prometheus is queried.
  // Configure aliases/instances in Settings → Hosts.
  const hosts = (latestReport && latestReport.host_catalog) || {};
  const sel = currentInstanceSelection(document.querySelector("#edit-query")?.value || "");
  const chips = [`<button type="button" class="prom-chip${sel.mode === "all" ? " on" : ""}" data-inst="*">todos</button>`];
  Object.entries(hosts).forEach(([name, host]) => {
    const inst = host.prometheus_instance || name;
    const label = host.alias || name;
    const on = sel.mode !== "all" && sel.set.has(inst);
    chips.push(`<button type="button" class="prom-chip${on ? " on" : ""}" data-inst="${escapeAttr(inst)}" title='instance="${escapeAttr(inst)}"'>${escapeHtml(label)}</button>`);
  });
  box.innerHTML = chips.join("");
}

function parsePromExpr(q) {
  const m = String(q || "").match(/^([\s\S]*?)(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$/);
  if (m) return { metric: m[1].trim(), op: m[2], threshold: parseFloat(m[3]) };
  return { metric: String(q || "").trim(), op: null, threshold: null };
}

function fmtNum(v) {
  if (!isFinite(v)) return "—";
  const a = Math.abs(v);
  if (a !== 0 && (a < 0.01 || a >= 100000)) return v.toExponential(1);
  return (Math.round(v * 100) / 100).toString();
}

function drawPromChart(container, series, threshold, t0, t1) {
  const W = container.clientWidth || 560;
  const H = 150, padL = 46, padR = 10, padT = 10, padB = 18;
  let ymin = Infinity, ymax = -Infinity;
  series.forEach((s) => s.values.forEach(([, v]) => {
    const n = parseFloat(v);
    if (isFinite(n)) { ymin = Math.min(ymin, n); ymax = Math.max(ymax, n); }
  }));
  if (threshold != null) { ymin = Math.min(ymin, threshold); ymax = Math.max(ymax, threshold); }
  if (!isFinite(ymin)) { container.innerHTML = '<div class="prom-empty">sin datos para esta métrica</div>'; return; }
  if (ymin === ymax) { ymax = ymin + 1; ymin = ymin - 1; }
  const padY = (ymax - ymin) * 0.1; ymin -= padY; ymax += padY;
  const X = (t) => padL + ((t - t0) / (t1 - t0 || 1)) * (W - padL - padR);
  const Y = (v) => padT + (1 - (v - ymin) / (ymax - ymin || 1)) * (H - padT - padB);
  const colors = ["#6aa3ff", "#46c97e", "#e0a64b", "#b07ce0", "#d6453c"];
  let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">`;
  svg += `<line x1="${padL}" y1="${padT}" x2="${padL}" y2="${H - padB}" stroke="#333"/>`;
  svg += `<line x1="${padL}" y1="${H - padB}" x2="${W - padR}" y2="${H - padB}" stroke="#333"/>`;
  svg += `<text x="3" y="${Y(ymax) + 4}" fill="#888" font-size="9">${fmtNum(ymax)}</text>`;
  svg += `<text x="3" y="${Y(ymin) + 4}" fill="#888" font-size="9">${fmtNum(ymin)}</text>`;
  if (threshold != null) {
    const ty = Y(threshold);
    svg += `<line x1="${padL}" y1="${ty}" x2="${W - padR}" y2="${ty}" stroke="#d6453c" stroke-width="1.2" stroke-dasharray="5 4"/>`;
    svg += `<text x="${W - padR}" y="${ty - 3}" fill="#d6453c" font-size="9" text-anchor="end">thr ${fmtNum(threshold)}</text>`;
  }
  series.forEach((s, i) => {
    const pts = s.values
      .map(([t, v]) => [X(t), Y(parseFloat(v))])
      .filter(([, y]) => isFinite(y))
      .map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`)
      .join(" ");
    if (pts) svg += `<polyline points="${pts}" fill="none" stroke="${colors[i % colors.length]}" stroke-width="1.5"/>`;
  });
  svg += "</svg>";
  container.innerHTML = svg;
  const legend = document.querySelector("#prom-preview-legend");
  if (legend) {
    legend.innerHTML = series.slice(0, 6).map((s, i) => {
      const name = s.metric.instance || s.metric.__name__ || Object.values(s.metric)[0] || "serie";
      const last = s.values.length ? fmtNum(parseFloat(s.values[s.values.length - 1][1])) : "—";
      return `<span class="prom-leg"><i style="background:${colors[i % colors.length]}"></i>${escapeHtml(String(name))}: ${last}</span>`;
    }).join("");
  }
}

async function refreshPromPreview() {
  const box = document.querySelector("#prom-preview");
  if (!box || box.style.display === "none") return;
  const chart = document.querySelector("#prom-preview-chart");
  const statusEl = document.querySelector("#prom-preview-status");
  const query = (document.querySelector("#edit-query")?.value || "").trim();
  if (!query) { chart.innerHTML = '<div class="prom-empty">escribe una query…</div>'; statusEl.textContent = ""; return; }
  const { metric, threshold } = parsePromExpr(query);
  const minutes = document.querySelector("#prom-preview-range")?.value || "60";
  const host = (document.querySelector("[data-target-name]:checked")?.dataset.targetName) || "localhost";
  statusEl.textContent = "…";
  statusEl.className = "prom-status";
  try {
    const params = new URLSearchParams({ query: metric || query, expr: query, minutes, host });
    const resp = await fetch(`/api/prom_range?${params.toString()}`);
    const data = await resp.json();
    if (!data.ok) { chart.innerHTML = `<div class="prom-empty">${escapeHtml(data.error || "error")}</div>`; statusEl.textContent = ""; return; }
    const series = (data.data && data.data.result) || [];
    const t0 = data.start, t1 = data.end;
    drawPromChart(chart, series, threshold, t0, t1);
    renderPromHosts();
    if (typeof data.firing === "boolean") {
      statusEl.textContent = data.firing ? "🔴 saltaría ahora" : "🟢 no saltaría";
      statusEl.className = data.firing ? "prom-status fire" : "prom-status ok";
      statusEl.title = data.firing_detail || "";
    } else {
      statusEl.textContent = "";
    }
  } catch (err) {
    chart.innerHTML = `<div class="prom-empty">${escapeHtml(err.message)}</div>`;
    statusEl.textContent = "";
  }
}

function wirePromPreview() {
  if (promPreviewWired) return;
  promPreviewWired = true;
  document.querySelector("#edit-query")?.addEventListener("input", () => {
    clearTimeout(promPreviewTimer);
    promPreviewTimer = setTimeout(refreshPromPreview, 500);
  });
  document.querySelector("#prom-preview-range")?.addEventListener("change", refreshPromPreview);
  document.querySelector("#prom-preview-refresh")?.addEventListener("click", refreshPromPreview);
  document.querySelector("#prom-hosts")?.addEventListener("click", (e) => {
    const chip = e.target.closest(".prom-chip");
    if (!chip) return;
    const query = document.querySelector("#edit-query")?.value || "";
    if (chip.dataset.inst === "*") {
      setPromQuery(applyInstanceToQuery(query, 'instance=~".*"'));
      return;
    }
    const sel = currentInstanceSelection(query);
    const set = sel.mode === "all" ? new Set() : new Set(sel.set);
    if (set.has(chip.dataset.inst)) set.delete(chip.dataset.inst);
    else set.add(chip.dataset.inst);
    setPromQuery(applyInstanceToQuery(query, instanceMatcherFor(set, false)));
  });
}

// ── Trigger list + chained action builder (Alexa-routine style) ────────────
let editorActionChain = [];
let editorExtraTriggers = [];
let editorAutoRemediate = true; // preserved per-check (no UI toggle; AI runs only if an AI Agent action exists)
let chainControlsWired = false;

const ACTION_FIELD_SPECS = {
  notification: [
    { k: "channels", t: "checks", opts: ["email", "push"], label: "Channels" },
    { k: "to", t: "text", label: "Email recipient (vacío = el de Settings)" },
    { k: "subject", t: "text", label: "Subject" },
    { k: "message", t: "text", label: "Message ({name} {target} {detail} {result})" },
  ],
  // AI Agent config (agents / token usage / fix prompt / emergency) is the
  // relocatable #ai-agent-config block moved into this card; no inline fields.
  ai_agent: [],
  bash: [
    { k: "command", t: "text", label: "Command" },
    { k: "target", t: "text", label: "Run on host (blank = check target, 'localhost' = local)" },
    { k: "timeout", t: "num", label: "Timeout (s)" },
    { k: "marks_fixed", t: "bool", label: "Mark check fixed if it succeeds" },
  ],
  docker: [
    { k: "action", t: "select", opts: ["restart", "start", "stop"], label: "Action" },
    { k: "name", t: "text", label: "Container name" },
    { k: "target", t: "text", label: "Host (blank = check target)" },
    { k: "marks_fixed", t: "bool", label: "Mark fixed if it succeeds" },
  ],
  systemd: [
    { k: "action", t: "select", opts: ["restart", "start", "stop", "reload"], label: "Action" },
    { k: "unit", t: "text", label: "Unit" },
    { k: "scope", t: "select", opts: ["system", "user"], label: "Scope" },
    { k: "target", t: "text", label: "Host (blank = check target)" },
    { k: "marks_fixed", t: "bool", label: "Mark fixed if it succeeds" },
  ],
  http: [
    { k: "method", t: "select", opts: ["POST", "GET", "PUT"], label: "Method" },
    { k: "url", t: "text", label: "URL" },
    { k: "body", t: "json", label: "Body (JSON or text)" },
  ],
  wait: [{ k: "seconds", t: "num", label: "Seconds" }],
  recheck: [],
  silence: [
    { k: "minutes", t: "num", label: "Minutes" },
    { k: "reason", t: "text", label: "Reason" },
  ],
  escalate: [
    { k: "after_failures", t: "num", label: "After N consecutive failures" },
    { k: "severity", t: "select", opts: ["", "info", "warning", "high", "critical"], label: "Bump severity" },
    { k: "channels", t: "checks", opts: ["email", "push"], label: "Channels" },
    { k: "message", t: "text", label: "Message" },
  ],
  noop: [{ k: "note", t: "text", label: "Note" }],
};
const ACTION_WHEN_OPTS = ["on_alert", "always", "still_failing", "recovered", "no_internet"];
// Per-type fields for extra-trigger cards (label + type are always shown).
const TRIGGER_TYPE_SPECS = {
  ssh: [
    { k: "command", t: "text", label: "Command" },
    { k: "expect_empty", t: "bool", label: "La salida debe estar vacía" },
    { k: "expect_nonempty", t: "bool", label: "La salida no debe estar vacía" },
    { k: "expect_contains", t: "text", label: "La salida contiene" },
    { k: "expect_not_contains", t: "text", label: "La salida NO contiene" },
  ],
  local: [
    { k: "command", t: "text", label: "Command" },
    { k: "expect_empty", t: "bool", label: "La salida debe estar vacía" },
    { k: "expect_nonempty", t: "bool", label: "La salida no debe estar vacía" },
    { k: "expect_contains", t: "text", label: "La salida contiene" },
    { k: "expect_not_contains", t: "text", label: "La salida NO contiene" },
  ],
  http: [
    { k: "url", t: "text", label: "URL" },
    { k: "expect_contains", t: "text", label: "La respuesta debe contener" },
  ],
  prometheus_query: [
    { k: "query", t: "textarea", label: "PromQL (ej: node_load5 > 10)" },
  ],
  network_ping: [
    { k: "ping_targets", t: "json", label: "Ping targets JSON" },
  ],
};
const TRIGGER_HEAD_SPECS = [
  { k: "label", t: "text", label: "Label" },
  { k: "type", t: "select", opts: ["ssh", "local", "http", "prometheus_query", "network_ping"], label: "Type" },
];
function extraTriggerSpecs(type) {
  return TRIGGER_HEAD_SPECS.concat(TRIGGER_TYPE_SPECS[type] || TRIGGER_TYPE_SPECS.ssh);
}

function chainFieldHtml(s, obj) {
  const v = obj[s.k];
  if (s.t === "checks") {
    const boxes = s.opts
      .map((o) => `<label class="chain-check"><input type="checkbox" data-check="${s.k}" value="${o}" ${(v || []).includes(o) ? "checked" : ""}><span>${o}</span></label>`)
      .join("");
    return `<div class="chain-field"><span>${s.label}</span><div class="chain-checks">${boxes}</div></div>`;
  }
  if (s.t === "select") {
    const opts = s.opts.map((o) => `<option value="${o}" ${String(v || "") === o ? "selected" : ""}>${o || "—"}</option>`).join("");
    return `<label class="chain-field"><span>${s.label}</span><select data-field="${s.k}" data-kind="select">${opts}</select></label>`;
  }
  if (s.t === "bool") {
    return `<label class="chain-field chain-bool"><input type="checkbox" data-field="${s.k}" data-kind="bool" ${v ? "checked" : ""}><span>${s.label}</span></label>`;
  }
  if (s.t === "textarea" || s.t === "json") {
    const val = s.t === "json" && v != null && typeof v !== "string" ? JSON.stringify(v) : v ?? "";
    return `<label class="chain-field full"><span>${s.label}</span><textarea data-field="${s.k}" data-kind="${s.t}" rows="2">${escapeHtml(String(val))}</textarea></label>`;
  }
  return `<label class="chain-field"><span>${s.label}</span><input type="text" data-field="${s.k}" data-kind="${s.t}" value="${escapeAttr(String(v ?? ""))}"></label>`;
}

function chainWhenHtml(v) {
  const opts = ACTION_WHEN_OPTS.map((o) => `<option value="${o}" ${(v || "on_alert") === o ? "selected" : ""}>${o}</option>`).join("");
  return `<label class="chain-field"><span>When</span><select data-field="when" data-kind="select">${opts}</select></label>`;
}

function chainCtrlsHtml() {
  return `<span class="chain-summary-hint">opciones ▾</span><span class="chain-card-ctrls"><button type="button" class="chain-move" data-dir="up" title="Subir">↑</button><button type="button" class="chain-move" data-dir="down" title="Bajar">↓</button><button type="button" class="chain-remove" title="Borrar">✕</button></span>`;
}

function actionCardHtml(a, idx) {
  const specs = ACTION_FIELD_SPECS[a.type] || [];
  const fields = specs.map((s) => chainFieldHtml(s, a)).join("");
  return `<details class="chain-card" data-kind="action" data-type="${escapeAttr(a.type || "")}" data-idx="${idx}">
    <summary class="chain-card-head"><span class="chain-badge">${idx + 1}) ${escapeHtml(a.type || "")}</span>${chainCtrlsHtml()}</summary>
    <div class="chain-card-body">${fields}${chainWhenHtml(a.when)}</div></details>`;
}

function triggerCardHtml(t, idx) {
  const type = t.type || "ssh";
  const fields = extraTriggerSpecs(type).map((s) => chainFieldHtml(s, t)).join("");
  return `<details class="chain-card" data-kind="trigger" data-type="${escapeAttr(type)}" data-idx="${idx}">
    <summary class="chain-card-head"><span class="chain-badge">${idx + 2}) ${escapeHtml(t.label || type)}</span>${chainCtrlsHtml()}</summary>
    <div class="chain-card-body">${fields}</div></details>`;
}

function readChainCard(card, specs) {
  const obj = { type: card.dataset.type };
  const whenEl = card.querySelector('[data-field="when"]');
  if (whenEl) obj.when = whenEl.value;
  specs.forEach((s) => {
    if (s.t === "checks") {
      obj[s.k] = [...card.querySelectorAll(`[data-check="${s.k}"]:checked`)].map((n) => n.value);
      return;
    }
    const el = card.querySelector(`[data-field="${s.k}"]`);
    if (!el) return;
    if (s.t === "bool") { obj[s.k] = el.checked; return; }
    let val = el.value;
    if (s.t === "num") { if (String(val).trim() === "") return; obj[s.k] = Number(val); return; }
    if (s.t === "csv") { obj[s.k] = val.split(",").map((x) => x.trim()).filter(Boolean); return; }
    if (s.t === "json") { val = val.trim(); if (!val) return; try { obj[s.k] = JSON.parse(val); } catch { obj[s.k] = val; } return; }
    if (String(val).trim() !== "") obj[s.k] = val;
  });
  return obj;
}

function collectActionChain() {
  return [...document.querySelectorAll("#actions-chain-list .chain-card")].map((card) => readChainCard(card, ACTION_FIELD_SPECS[card.dataset.type] || []));
}
function collectExtraTriggers() {
  return [...document.querySelectorAll("#extra-triggers-list .chain-card")].map((card) => readChainCard(card, extraTriggerSpecs(card.dataset.type)));
}

function placeAiAgentConfig() {
  const block = document.getElementById("ai-agent-config");
  const holder = document.getElementById("ai-agent-config-holder");
  if (!block || !holder) return;
  const aiBody = document.querySelector('#actions-chain-list .chain-card[data-type="ai_agent"] .chain-card-body');
  if (aiBody) aiBody.appendChild(block);
  else if (block.parentElement !== holder) holder.appendChild(block);
}

function renderActionChain() {
  const c = document.querySelector("#actions-chain-list");
  if (!c) return;
  // Rescue the relocatable AI-agent config block before innerHTML wipes the cards,
  // otherwise resetting innerHTML would destroy its inputs (#edit-fix-prompt, etc.).
  const block = document.getElementById("ai-agent-config");
  const holder = document.getElementById("ai-agent-config-holder");
  if (block && holder) holder.appendChild(block);
  c.innerHTML = editorActionChain.length
    ? editorActionChain.map((a, i) => actionCardHtml(a, i)).join("")
    : `<p class="chain-empty">Sin acciones: el check solo alerta/notifica. Añade una acción abajo.</p>`;
  attachAlertAutosaveListeners();
  placeAiAgentConfig();
}
function renderExtraTriggers() {
  const c = document.querySelector("#extra-triggers-list");
  if (!c) return;
  c.innerHTML = editorExtraTriggers.length
    ? editorExtraTriggers.map((t, i) => triggerCardHtml(t, i)).join("")
    : `<p class="chain-empty">Solo el trigger primario (formulario de arriba).</p>`;
  attachAlertAutosaveListeners();
}

function defaultAction(t) {
  const d = { type: t, when: "on_alert" };
  if (t === "notification") d.channels = ["email"];
  if (t === "wait") d.seconds = 20;
  if (t === "silence") d.minutes = 30;
  if (t === "escalate") { d.after_failures = 3; d.channels = ["email"]; }
  if (t === "docker" || t === "systemd") d.action = "restart";
  if (t === "http") d.method = "POST";
  return d;
}

function handleChainClick(e, kind) {
  const card = e.target.closest(".chain-card");
  if (!card) return;
  const remove = e.target.closest(".chain-remove");
  const move = e.target.closest(".chain-move");
  if (!remove && !move) return;
  // These controls live inside the <summary>; stop the native details toggle.
  e.preventDefault();
  e.stopPropagation();
  const idx = Number(card.dataset.idx);
  const arr = kind === "action" ? (editorActionChain = collectActionChain()) : (editorExtraTriggers = collectExtraTriggers());
  if (remove) {
    arr.splice(idx, 1);
  } else {
    const j = move.dataset.dir === "up" ? idx - 1 : idx + 1;
    if (j < 0 || j >= arr.length) return;
    [arr[idx], arr[j]] = [arr[j], arr[idx]];
  }
  kind === "action" ? renderActionChain() : renderExtraTriggers();
  scheduleAlertAutosave();
}

function toggleAddMenu(menu) {
  if (!menu) return;
  const willShow = menu.hidden;
  document.querySelectorAll(".add-menu").forEach((m) => (m.hidden = true));
  menu.hidden = !willShow;
}

function wireChainControls() {
  if (chainControlsWired) return;
  chainControlsWired = true;
  const actMenu = document.querySelector("#add-action-menu");
  const trgMenu = document.querySelector("#add-trigger-menu");
  document.querySelector("#add-action-button")?.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleAddMenu(actMenu);
  });
  document.querySelector("#add-trigger-button")?.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleAddMenu(trgMenu);
  });
  actMenu?.addEventListener("click", (e) => {
    const item = e.target.closest(".add-menu-item");
    if (!item) return;
    editorActionChain = collectActionChain();
    editorActionChain.push(defaultAction(item.dataset.type));
    actMenu.hidden = true;
    renderActionChain();
    scheduleAlertAutosave();
  });
  trgMenu?.addEventListener("click", (e) => {
    const item = e.target.closest(".add-menu-item");
    if (!item) return;
    editorExtraTriggers = collectExtraTriggers();
    editorExtraTriggers.push({ type: item.dataset.ttype, label: item.dataset.ttype });
    trgMenu.hidden = true;
    renderExtraTriggers();
    scheduleAlertAutosave();
  });
  // Close any open add-menu when clicking elsewhere.
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".add-menu-wrap")) {
      document.querySelectorAll(".add-menu").forEach((m) => (m.hidden = true));
    }
  });
  document.querySelector("#actions-chain-list")?.addEventListener("click", (e) => handleChainClick(e, "action"));
  document.querySelector("#extra-triggers-list")?.addEventListener("click", (e) => handleChainClick(e, "trigger"));
  // Changing a trigger card's type re-renders it with that type's fields.
  document.querySelector("#extra-triggers-list")?.addEventListener("change", (e) => {
    if (!e.target.matches('[data-field="type"]')) return;
    editorExtraTriggers = collectExtraTriggers();
    renderExtraTriggers();
    scheduleAlertAutosave();
  });
}

function buildPrimaryTrigger() {
  const v = (sel) => (document.querySelector(sel)?.value || "").trim();
  const t = { type: v("#edit-type") || "ssh", label: "primary" };
  const cmd = v("#edit-command"); if (cmd) t.command = cmd;
  const url = v("#edit-url"); if (url) t.url = url;
  const q = v("#edit-query"); if (q) t.query = q;
  const cmp = v("#edit-comparator"); if (cmp) t.comparator = cmp;
  const th = v("#edit-threshold"); if (th !== "") t.threshold = Number(th);
  if (document.querySelector("#edit-expect-empty")?.checked) t.expect_empty = true;
  if (document.querySelector("#edit-expect-nonempty")?.checked) t.expect_nonempty = true;
  return t;
}

function renderEditor(alert) {
  const config = alert.config || {};
  const actualCommand = config.command || "";
  const preview = {
    id: alert.id,
    name: alert.name,
    command: actualCommand || config.query || config.url || config.type || "check",
    schedule: config.schedule || "*/5 * * * *",
    severity: severityMap[(config.severity || "info").toLowerCase()] || "Info",
    timeout: config.timeout || 30,
    notifications: config.notifications ? "Enabled" : "Disabled",
    targets: alert.targets,
  };

  document.querySelector("#edit-name").value = preview.name;
  document.querySelector("#edit-command").value = actualCommand;
  document.querySelector("#edit-schedule").value = preview.schedule;
  document.querySelector("#edit-severity").value = (config.severity || "info").toLowerCase();
  document.querySelector("#edit-timeout").value = String(preview.timeout);
  document.querySelector("#edit-notifications").checked = Boolean(config.notifications ?? true);
  document.querySelector("#edit-mobile-visible").checked = Boolean(config.mobile_visible ?? true);
  document.querySelector("#edit-mobile-notify").checked = Boolean(config.mobile_notify ?? config.notifications ?? true);
  document.querySelector("#edit-description").value = config.description || alert.description || alert.name;
  document.querySelector("#edit-type").value = config.type || "ssh";
  document.querySelector("#edit-url").value = config.url || "";
  const expectEl = document.querySelector("#edit-expect-contains");
  if (expectEl) expectEl.value = config.expect_contains || "";
  document.querySelector("#edit-query").value = config.query || "";
  document.querySelector("#edit-alertmanager-url").value = config.alertmanager_url || "";
  document.querySelector("#edit-alertmanager-filter").value = config.alertmanager_filter ? JSON.stringify(config.alertmanager_filter) : "";
  document.querySelector("#edit-filter-silenced").checked = config.filter_silenced !== false;
  document.querySelector("#edit-filter-inhibited").checked = config.filter_inhibited !== false;
  // ssh/local: derive the "how to evaluate output" mode from the saved assertions.
  const sshEvalSel = document.querySelector("#edit-ssh-eval");
  if (sshEvalSel) {
    let mode = "none";
    if (config.expect_contains) mode = "contains";
    else if (config.expect_not_contains) mode = "not_contains";
    else if (config.expect_empty) mode = "empty";
    else if (config.expect_nonempty) mode = "nonempty";
    sshEvalSel.value = mode;
    const matchEl = document.querySelector("#edit-ssh-match-text");
    if (matchEl) matchEl.value = config.expect_contains || config.expect_not_contains || "";
  }
  updateTypeSpecificFields(config.type || "ssh");
  document.querySelector("#edit-threshold").value = config.threshold ?? "";
  document.querySelector("#edit-threshold-query").value = config.threshold_query || "";
  document.querySelector("#edit-comparator").value = config.comparator || "";
  document.querySelector("#edit-accept-codes").value = (config.accept_codes || []).join(",");
  document.querySelector("#edit-ignore-targets").value = (config.ignore_targets || []).join(",");
  document.querySelector("#edit-expect-empty").checked = Boolean(config.expect_empty);
  document.querySelector("#edit-expect-nonempty").checked = Boolean(config.expect_nonempty);
  document.querySelector("#edit-parse-cert-days").checked = Boolean(config.parse_cert_days);
  document.querySelector("#edit-cert-warn-days").value = config.cert_warn_days ?? "";
  document.querySelector("#edit-steps").value = JSON.stringify(config.steps || [], null, 2);
  document.querySelector("#edit-fix-prompt").value = config.fix_prompt || "";
  document.querySelector("#edit-emergency-actions").value = JSON.stringify(config.emergency_actions || [], null, 2);
  // New trigger/action model
  const pingEl = document.querySelector("#edit-ping-targets");
  if (pingEl) pingEl.value = JSON.stringify(config.ping_targets || [], null, 2);
  editorAutoRemediate = config.auto_remediate ?? true;
  const trg = config.triggers;
  if (trg && Array.isArray(trg.list) && trg.list.length) {
    document.querySelector("#edit-trigger-match").value = trg.match === "all" ? "all" : "any";
    editorExtraTriggers = trg.list.slice(1).map((x) => ({ ...x }));
  } else {
    if (document.querySelector("#edit-trigger-match")) document.querySelector("#edit-trigger-match").value = "any";
    editorExtraTriggers = [];
  }
  editorActionChain = Array.isArray(config.actions) ? config.actions.map((x) => ({ ...x })) : [];
  renderExtraTriggers();
  renderActionChain();
  wireChainControls();
  const tokenProtection = config.token_protection || {};
  document.querySelector("#token-protection-enabled").checked = Boolean(tokenProtection.enabled ?? true);
  document.querySelector("#token-max-prompt").value = tokenProtection.max_prompt_tokens ?? 4000;
  document.querySelector("#token-max-response").value = tokenProtection.max_response_tokens ?? 4000;
  document.querySelector("#token-max-total").value = tokenProtection.max_total_tokens_per_run ?? 12000;
  document.querySelector("#token-notify-stop").checked = Boolean(tokenProtection.notify_on_stop ?? true);
  setAgentCheckboxes(config);
  loadExcludesFromConfig(config);
  const previewCmdEl = document.querySelector("#edit-preview-command");
  if (previewCmdEl) previewCmdEl.value = config.preview_command || "";

  setText("#preview-name", preview.name);
  setText("#preview-command", preview.command);
  setText("#preview-schedule", preview.schedule);
  setText("#preview-severity", preview.severity);
  setText("#preview-timeout", `${preview.timeout}s`);
  setText("#preview-notifications", preview.notifications);

  const payload = {
    name: preview.name,
    command: preview.command,
    schedule: preview.schedule,
    severity: preview.severity.toLowerCase(),
    timeout: preview.timeout,
    notifications: config.notifications ?? true,
    targets: preview.targets,
    id: preview.id,
  };
  const formatted = JSON.stringify(payload, null, 2);
  jsonPreview.textContent = formatted;
  setText("#preview-json", formatted);
  rearmAlertButton.disabled = !alert.checks?.some((check) => check.alert_state?.schedule_paused);
  applyEditorLockState(Boolean(config.locked));
  if (!alertAutosaveInFlight) setSaveStatusText("Autosave idle");
}

// When a check is locked, freeze its identity/shape in the editor: name, type,
// targets, steps and the trigger/action chain composition. Minor tuning fields
// (query, threshold, schedule, severity, fix_prompt, token/agents…) stay
// editable so the autosave keeps working. The backend enforces the same set.
function applyEditorLockState(locked) {
  const structural = [
    "#edit-name", "#edit-type", "#edit-steps", "#edit-trigger-match",
    "#add-trigger-button", "#add-action-button",
  ];
  structural.forEach((sel) => { const el = document.querySelector(sel); if (el) el.disabled = locked; });
  document.querySelectorAll("[data-target-name]").forEach((el) => { el.disabled = locked; });
  // Chain composition controls (reorder/remove/type/when). The ai_agent config
  // (#ai-agent-config: fix_prompt/agents/token) is top-level/minor → stays editable.
  document.querySelectorAll(
    "#extra-triggers-list button, #extra-triggers-list select, #actions-chain-list button, #actions-chain-list select",
  ).forEach((el) => {
    if (el.closest("#ai-agent-config")) return;
    el.disabled = locked;
  });
  if (deleteAlertButton) deleteAlertButton.disabled = locked;
  const lockBtn = document.querySelector("#lock-alert-button");
  if (lockBtn) {
    // Keep the button visible in both states so it can be hovered for the
    // tooltip; it toggles lock/unlock and reflects the current state.
    lockBtn.hidden = false;
    lockBtn.textContent = locked ? "🔓 Unlock" : "🔒 Lock";
    lockBtn.classList.add("has-tooltip");
    lockBtn.dataset.locked = locked ? "true" : "false";
    lockBtn.dataset.tooltip = locked
      ? "Check bloqueado: nombre, tipo, targets, steps y las cadenas de triggers/actions están protegidos, y no se puede borrar. Los ajustes menores (query, threshold, schedule…) siguen guardándose. Click para desbloquear."
      : "Bloquea la identidad/forma del check (nombre, tipo, targets, steps, triggers/actions) y evita borrarlo. Los ajustes menores siguen editables.";
  }
  const form = document.querySelector("#alert-editor-form");
  if (form) form.classList.toggle("is-locked", locked);
}

async function setAlertLock(locked) {
  const selected = getSelectedAlert(latestReport);
  if (!selected) return;
  if (!locked && !confirm(`¿Desbloquear "${selected.name}"? Volverá a ser editable y borrable.`)) return;
  try {
    const response = await fetch("/api/alert/toggle-lock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: selected.id, name: selected.name, locked }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "failed");
    if (latestReport && Array.isArray(data.alert_rules)) latestReport.alert_rules = data.alert_rules;
    showToast(locked ? "Check bloqueado" : "Check desbloqueado", "success");
    if (latestReport) render(latestReport);
  } catch (error) {
    showToast(`No se pudo cambiar el lock: ${error.message}`, "error");
  }
}

// ── Per-host Excludes ──────────────────────────────────────────

let hostExcludes = {}; // { hostName: [pattern, ...] }

function renderExcludesSection(targets) {
  const container = document.querySelector("#excludes-host-rows");
  if (!container) return;
  const rows = ["*", ...(targets || [])];
  container.innerHTML = rows.map((host) => buildExcludeRow(host)).join("");
  container.querySelectorAll(".exclude-tag-input").forEach(attachExcludeInputListeners);
}

function buildExcludeRow(host) {
  const tags = (hostExcludes[host] || []).map((p) => buildExcludeTag(host, p)).join("");
  const isAll = host === "*";
  const badgeClass = isAll ? "excludes-host-badge badge-all" : "excludes-host-badge";
  const badgeIcon = isAll
    ? `<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="6" cy="6" r="5"/><path d="M6 1v10M1 6h10"/></svg>`
    : `<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="1" y="2" width="10" height="8" rx="1.5"/><path d="M4 2V1M8 2V1"/></svg>`;
  const label = isAll ? "All hosts  *" : host;
  const hint = isAll ? "Applies to every host" : "";
  return `<div class="excludes-host-row" data-exclude-host="${escapeAttr(host)}">
    <div class="excludes-host-label">
      <span class="${badgeClass}">${badgeIcon}${escapeHtml(label)}</span>
      ${hint ? `<span class="excludes-empty-hint">${hint}</span>` : ""}
    </div>
    <div class="excludes-tag-area">
      ${tags}
      <input class="exclude-tag-input" data-host="${escapeAttr(host)}" placeholder="type pattern, press Enter…" autocomplete="off" spellcheck="false">
    </div>
  </div>`;
}

function buildExcludeTag(host, pattern) {
  return `<span class="exclude-tag" data-host="${escapeAttr(host)}" data-pattern="${escapeAttr(pattern)}">
    ${escapeHtml(pattern)}
    <button type="button" class="exclude-tag-remove" aria-label="Remove" data-host="${escapeAttr(host)}" data-pattern="${escapeAttr(pattern)}">✕</button>
  </span>`;
}

function attachExcludeInputListeners(input) {
  input.addEventListener("keydown", (e) => {
    const host = input.dataset.host;
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addExcludeTag(host, input.value);
      input.value = "";
    } else if (e.key === "Backspace" && !input.value) {
      const tags = hostExcludes[host] || [];
      if (tags.length) {
        removeExcludeTag(host, tags[tags.length - 1]);
      }
    }
  });
  input.addEventListener("blur", () => {
    const host = input.dataset.host;
    if (input.value.trim()) {
      addExcludeTag(host, input.value);
      input.value = "";
    }
  });
}

function addExcludeTag(host, raw) {
  const pattern = raw.trim().replace(/,$/, "").trim();
  if (!pattern) return;
  if (!hostExcludes[host]) hostExcludes[host] = [];
  if (hostExcludes[host].includes(pattern)) return;
  hostExcludes[host].push(pattern);
  refreshExcludeRow(host);
  scheduleAlertAutosave();
}

function removeExcludeTag(host, pattern) {
  if (!hostExcludes[host]) return;
  hostExcludes[host] = hostExcludes[host].filter((p) => p !== pattern);
  refreshExcludeRow(host);
  scheduleAlertAutosave();
}

function refreshExcludeRow(host) {
  const row = document.querySelector(`.excludes-host-row[data-exclude-host="${CSS.escape(host)}"]`);
  if (!row) return;
  const tagArea = row.querySelector(".excludes-tag-area");
  const input = tagArea.querySelector(".exclude-tag-input");
  const tags = (hostExcludes[host] || []).map((p) => buildExcludeTag(host, p)).join("");
  tagArea.innerHTML = tags + `<input class="exclude-tag-input" data-host="${escapeAttr(host)}" placeholder="type pattern, press Enter…" autocomplete="off" spellcheck="false">`;
  const newInput = tagArea.querySelector(".exclude-tag-input");
  attachExcludeInputListeners(newInput);
  tagArea.querySelectorAll(".exclude-tag-remove").forEach((btn) => {
    btn.addEventListener("click", () => removeExcludeTag(btn.dataset.host, btn.dataset.pattern));
  });
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest(".exclude-tag-remove");
  if (btn) removeExcludeTag(btn.dataset.host, btn.dataset.pattern);
});

function loadExcludesFromConfig(config) {
  hostExcludes = {};
  const hp = config.host_params || {};
  for (const [host, params] of Object.entries(hp)) {
    const raw = params.exclude || "";
    if (raw) hostExcludes[host] = raw.split("|").map((s) => s.trim()).filter(Boolean);
  }
}

function gatherHostParams() {
  const result = {};
  for (const [host, patterns] of Object.entries(hostExcludes)) {
    if (patterns.length) result[host] = { exclude: patterns.join("|") };
  }
  return Object.keys(result).length ? result : undefined;
}

// ── Diagnostic Preview Section ─────────────────────────────

function extractAddToken(line) {
  const t = line.trim().split(/\s+/)[0] || "";
  return t.replace(/[:,%]+$/, "");
}

function buildPreviewLine(target, line) {
  const token = extractAddToken(line);
  return `<div class="preview-line">
    <span class="preview-line-text">${escapeHtml(line)}</span>
    ${token ? `<button type="button" class="preview-line-add" data-target="${escapeAttr(target)}" data-token="${escapeAttr(token)}" title="Add '${escapeAttr(token)}' to excludes">+</button>` : ""}
  </div>`;
}

function buildPreviewHostBlock(target, output, ranAt) {
  const lines = (output || "").split("\n").filter((l) => l.trim());
  const bodyHtml = lines.length
    ? lines.map((l) => buildPreviewLine(target, l)).join("")
    : `<div class="preview-output-empty">No output yet — click Refresh to run</div>`;
  const timeLabel = ranAt ? `Last run: ${formatRelativeTime(ranAt)}` : "Not run yet";
  return `<div class="preview-host-row" data-preview-target="${escapeAttr(target)}">
    <div class="preview-host-header">
      <span class="preview-host-badge">
        <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="1" y="2" width="10" height="8" rx="1.5"/><path d="M4 2V1M8 2V1"/></svg>
        ${escapeHtml(target)}
      </span>
      <span class="preview-host-timestamp">${escapeHtml(timeLabel)}</span>
      <button type="button" class="preview-refresh-btn" data-preview-target="${escapeAttr(target)}">
        <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 6A4 4 0 1 1 6 2M10 2v4H6"/></svg>
        Refresh
      </button>
    </div>
    <div class="preview-output">${bodyHtml}</div>
  </div>`;
}

function formatRelativeTime(iso) {
  if (!iso) return "unknown";
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function renderPreviewSection(alert, report) {
  const container = document.querySelector("#preview-host-rows");
  if (!container) return;
  const targets = alert.targets || [];
  if (!targets.length) { container.innerHTML = ""; return; }

  const checksByTarget = Object.fromEntries(
    (alert.checks || []).map((c) => [c.target, c])
  );

  container.innerHTML = targets.map((t) => {
    const check = checksByTarget[t] || {};
    return buildPreviewHostBlock(t, check.last_run_output || "", check.last_run_output ? report.timestamp : "");
  }).join("");

  attachPreviewListeners(alert.name, container);
}

function attachPreviewListeners(alertName, container) {
  container.querySelectorAll(".preview-refresh-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = btn.dataset.previewTarget;
      const previewCmd = document.querySelector("#edit-preview-command")?.value?.trim() || "";
      btn.classList.add("loading");
      btn.disabled = true;
      try {
        const res = await fetch("/api/alert/run-preview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: alertName, target, preview_override: previewCmd }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Preview failed");
        const row = container.querySelector(`.preview-host-row[data-preview-target="${CSS.escape(target)}"]`);
        if (row) {
          const lines = (data.output || "").split("\n").filter((l) => l.trim());
          const bodyHtml = lines.length
            ? lines.map((l) => buildPreviewLine(target, l)).join("")
            : `<div class="preview-output-empty">Empty output</div>`;
          row.querySelector(".preview-output").innerHTML = bodyHtml;
          row.querySelector(".preview-host-timestamp").textContent = `Last run: just now`;
          attachPreviewAddButtons(container, alertName);
        }
      } catch (err) {
        const row = container.querySelector(`.preview-host-row[data-preview-target="${CSS.escape(target)}"]`);
        if (row) row.querySelector(".preview-output").innerHTML = `<div class="preview-output-empty" style="color:var(--error,#e06c75)">${escapeHtml(String(err.message || err))}</div>`;
      } finally {
        btn.classList.remove("loading");
        btn.disabled = false;
      }
    });
  });
  attachPreviewAddButtons(container, alertName);
}

function attachPreviewAddButtons(container, alertName) {
  container.querySelectorAll(".preview-line-add").forEach((btn) => {
    btn.replaceWith(btn.cloneNode(true));
  });
  container.querySelectorAll(".preview-line-add").forEach((btn) => {
    btn.addEventListener("click", () => {
      const token = btn.dataset.token;
      const target = btn.dataset.target;
      if (!token) return;
      addExcludeTag(target, token);
      btn.classList.add("added");
      btn.textContent = "✓";
      setTimeout(() => { btn.classList.remove("added"); btn.textContent = "+"; }, 1400);
    });
  });
}

function renderTargetChoices(alert, report) {
  const selected = new Set(alert.targets || []);
  const hosts = Object.entries(report.host_catalog || {});
  const container = document.querySelector("#edit-targets");
  container.innerHTML = hosts.map(([name, host]) => `
    <label class="choice-item">
      <span>
        <strong>${name}</strong><br>
        <small>${host.address || "-"}</small>
      </span>
      <input type="checkbox" data-target-name="${name}" ${selected.has(name) ? "checked" : ""}>
    </label>
  `).join("");
  container.querySelectorAll("[data-target-name]").forEach((node) => {
    node.addEventListener("change", () => {
      const targets = [...document.querySelectorAll("[data-target-name]:checked")].map((n) => n.dataset.targetName);
      renderExcludesSection(targets);
      scheduleAlertAutosave();
    });
  });
  renderExcludesSection([...selected]);
}

// Fields touched since the last successful save — flashed green (or red) once
// the save resolves so each edit gets immediate per-field confirmation.
const pendingSavedFields = new Set();

function markFieldPending(el) {
  if (el) pendingSavedFields.add(el);
}

function flashSavedFields(tone) {
  const cls = tone === "error" ? "field-error" : "field-saved";
  pendingSavedFields.forEach((el) => {
    if (!el || !el.isConnected) return;
    el.classList.remove("field-saved", "field-error");
    void el.offsetWidth; // restart the transition
    el.classList.add(cls);
    setTimeout(() => el.classList.remove(cls), 1600);
  });
  pendingSavedFields.clear();
}

function isEditingAlertForm() {
  const a = document.activeElement;
  return Boolean(a && a.closest && a.closest("#alert-editor-form, .actions-form"));
}

function attachAlertAutosaveListeners() {
  document.querySelectorAll("#alert-editor-form input, #alert-editor-form textarea, #alert-editor-form select, .actions-form input, .actions-form textarea, .actions-form select").forEach((node) => {
    if (node.dataset.autosaveBound === "true") return;
    // Type while debounced; commit immediately when leaving the field (change/blur).
    node.addEventListener("input", () => { markFieldPending(node); scheduleAlertAutosave(); });
    node.addEventListener("change", () => { markFieldPending(node); flushAlertAutosave(); });
    node.dataset.autosaveBound = "true";
  });
}

function flushAlertAutosave() {
  clearTimeout(alertAutosaveTimer);
  alertAutosaveTimer = null;
  void saveAlert({ silent: true });
}

function parseJsonField(selector, fallback = []) {
  const raw = document.querySelector(selector).value.trim();
  if (!raw) return fallback;
  return JSON.parse(raw);
}

function setMiniSaveStatus(el, message, tone = "idle") {
  if (!el) return;
  el.textContent = message;
  el.dataset.state = tone;
}

function setSaveStatusText(message, tone = "idle") {
  saveStatus.textContent = message;
  saveStatus.dataset.state = tone;
  // Mirror onto the Targets tab header so toggling a target shows feedback there
  // too (the main #save-status only lives in the Triggers tab).
  setMiniSaveStatus(document.querySelector("#targets-save-status"), message, tone);
}

// Generic autosave for a settings <form>: reuses its existing submit handler via
// requestSubmit() (works with no submit button), debounced like the alert editor.
function attachFormAutosave(form, statusEl, { debounce = 700 } = {}) {
  if (!form || form.dataset.autosaveBound === "true") return;
  let timer = null;
  const flush = () => { clearTimeout(timer); timer = null; form.requestSubmit(); };
  const schedule = () => {
    setMiniSaveStatus(statusEl, "Guardando…", "saving");
    clearTimeout(timer);
    timer = setTimeout(flush, debounce);
  };
  form.querySelectorAll("input, textarea, select").forEach((el) => {
    el.addEventListener("input", schedule);
    el.addEventListener("change", flush);
  });
  form.dataset.autosaveBound = "true";
}

function isEditingSettingsForm() {
  const a = document.activeElement;
  return Boolean(a && a.closest && a.closest(
    "#agents-settings-form, #pipeline-settings-form, #mobile-endpoint-form, #fcm-form",
  ));
}

// Lightweight toast feedback so actions (rearm / re-run / ack / silence) always
// confirm whether they actually ran, on any tab — the save-status text only
// lives in the editor pane.
function showToast(message, tone = "info", timeout = 5000) {
  const container = document.querySelector("#toast-container");
  if (!container) {
    console.log(`[toast:${tone}] ${message}`);
    return;
  }
  const toast = document.createElement("div");
  toast.className = `toast toast-${tone}`;
  toast.setAttribute("role", "status");
  toast.textContent = message;
  const close = document.createElement("button");
  close.className = "toast-close";
  close.type = "button";
  close.setAttribute("aria-label", "Dismiss");
  close.textContent = "×";
  const dismiss = () => {
    toast.classList.add("toast-leaving");
    setTimeout(() => toast.remove(), 200);
  };
  close.addEventListener("click", dismiss);
  toast.appendChild(close);
  container.appendChild(toast);
  if (timeout) setTimeout(dismiss, timeout);
}

function hasPendingHostAutosave() {
  return hostAutosaveTimers.size > 0;
}

function shouldDeferRender(force = false) {
  if (force) return false;
  return alertFormDirty || alertAutosaveInFlight || alertAutosaveTimer !== null || hostFormDirty || hasPendingHostAutosave() || isEditingAlertForm() || isEditingSettingsForm();
}

function collectAllowedAgents() {
  const values = [];
  if (document.querySelector("#agent-claude").checked) values.push("claude");
  if (document.querySelector("#agent-codex").checked) values.push("codex");
  if (document.querySelector("#agent-opencode").checked) values.push("opencode");
  const customEnabled = document.querySelector("#agent-custom-enabled").checked;
  const customAgents = [];
  if (customEnabled) {
    const name = document.querySelector("#custom-agent-name").value.trim() || "custom-run";
    const commandTemplate = document.querySelector("#custom-agent-command").value.trim();
    if (commandTemplate) {
      values.push(name);
      customAgents.push({
        name,
        type: "custom",
        command_template: commandTemplate,
        enabled: true,
        timeout: Number(document.querySelector("#edit-timeout").value || 300),
        priority: 25,
        probe: false,
      });
    }
  }
  return { allowedAgents: values, customAgents };
}

function gatherAlertPayload() {
  const selected = isCreatingAlert ? null : getSelectedAlert(latestReport);
  const { allowedAgents, customAgents } = collectAllowedAgents();
  const actionChain = collectActionChain();
  const extraTriggers = collectExtraTriggers();
  // Output assertions: for ssh/local they come from the single "how to evaluate
  // output" selector; for other types keep the legacy checkbox/http behaviour.
  const evalType = document.querySelector("#edit-type").value;
  let outAssert;
  if (evalType === "ssh" || evalType === "local") {
    const mode = document.querySelector("#edit-ssh-eval")?.value || "none";
    const matchText = document.querySelector("#edit-ssh-match-text")?.value.trim() || "";
    outAssert = {
      expect_empty: mode === "empty",
      expect_nonempty: mode === "nonempty",
      expect_contains: mode === "contains" ? matchText : "",
      expect_not_contains: mode === "not_contains" ? matchText : "",
    };
  } else {
    outAssert = {
      expect_empty: document.querySelector("#edit-expect-empty").checked,
      expect_nonempty: document.querySelector("#edit-expect-nonempty").checked,
      expect_contains: document.querySelector("#edit-expect-contains")?.value.trim() || "",
      expect_not_contains: "",
    };
  }
  const payload = {
    original_id: selected?.id,
    original_name: selected?.name,
    alert_rule: {
      id: selected?.id,
      name: document.querySelector("#edit-name").value.trim(),
      description: document.querySelector("#edit-description").value.trim(),
      type: document.querySelector("#edit-type").value,
      schedule: document.querySelector("#edit-schedule").value.trim(),
      severity: document.querySelector("#edit-severity").value,
      timeout: Number(document.querySelector("#edit-timeout").value || 30),
      notifications: document.querySelector("#edit-notifications").checked,
      mobile_visible: document.querySelector("#edit-mobile-visible").checked,
      mobile_notify: document.querySelector("#edit-mobile-notify").checked,
      command: document.querySelector("#edit-command").value.trim(),
      preview_command: document.querySelector("#edit-preview-command")?.value?.trim() || "",
      url: document.querySelector("#edit-url").value.trim(),
      ...outAssert,
      query: document.querySelector("#edit-query").value.trim(),
      alertmanager_url: document.querySelector("#edit-alertmanager-url").value.trim(),
      alertmanager_filter: (() => { try { const raw = document.querySelector("#edit-alertmanager-filter").value.trim(); return raw ? JSON.parse(raw) : null; } catch { return null; } })(),
      filter_silenced: document.querySelector("#edit-filter-silenced").checked,
      filter_inhibited: document.querySelector("#edit-filter-inhibited").checked,
      threshold: document.querySelector("#edit-threshold").value.trim(),
      threshold_query: document.querySelector("#edit-threshold-query").value.trim(),
      comparator: document.querySelector("#edit-comparator").value,
      accept_codes: document.querySelector("#edit-accept-codes").value.split(",").map((item) => item.trim()).filter(Boolean),
      ignore_targets: document.querySelector("#edit-ignore-targets").value.split(",").map((item) => item.trim()).filter(Boolean),
      parse_cert_days: document.querySelector("#edit-parse-cert-days").checked,
      cert_warn_days: document.querySelector("#edit-cert-warn-days").value.trim(),
      steps: parseJsonField("#edit-steps", []),
      fix_prompt: document.querySelector("#edit-fix-prompt").value.trim(),
      targets: [...document.querySelectorAll("[data-target-name]:checked")].map((node) => node.dataset.targetName),
      allowed_agents: allowedAgents,
      custom_agents: customAgents,
      emergency_actions: parseJsonField("#edit-emergency-actions", []),
      pause_schedule_on_fix_failed: true,
      host_params: gatherHostParams(),
      auto_remediate: editorAutoRemediate,
      ping_targets: parseJsonField("#edit-ping-targets", []),
      actions: actionChain,
      token_protection: {
        enabled: document.querySelector("#token-protection-enabled").checked,
        max_prompt_tokens: Number(document.querySelector("#token-max-prompt").value || 4000),
        max_response_tokens: Number(document.querySelector("#token-max-response").value || 4000),
        max_total_tokens_per_run: Number(document.querySelector("#token-max-total").value || 12000),
        notify_on_stop: document.querySelector("#token-notify-stop").checked,
      },
    },
  };
  // Multi-trigger: primary (main form) + extra cards. Omit when there are no
  // extra triggers so single-trigger checks stay in their classic flat shape.
  if (extraTriggers.length) {
    payload.alert_rule.triggers = {
      match: document.querySelector("#edit-trigger-match")?.value === "all" ? "all" : "any",
      list: [buildPrimaryTrigger(), ...extraTriggers],
    };
  }
  return payload;
}

function canAutosaveAlert(payload) {
  return Boolean(payload.alert_rule.name && (payload.alert_rule.targets || []).length > 0);
}

function scheduleAlertAutosave() {
  if (!latestReport) return;
  alertFormDirty = true;
  clearTimeout(alertAutosaveTimer);
  setSaveStatusText("Saving...", "saving");
  alertAutosaveTimer = setTimeout(() => {
    alertAutosaveTimer = null;
    void saveAlert({ silent: true });
  }, 600);
}

async function saveAlert(opts = {}) {
  const { silent = false } = opts;
  try {
    const payload = gatherAlertPayload();
    if (!canAutosaveAlert(payload)) {
      setSaveStatusText("Draft incomplete: name + at least 1 target", "warning");
      return;
    }
    alertAutosaveInFlight = true;
    const response = await fetch("/api/alert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to save alert");
    setSaveStatusText("Saved", "saved");
    if (Array.isArray(data.locked_blocked) && data.locked_blocked.length) {
      showToast(`Cambio estructural ignorado (check bloqueado): ${data.locked_blocked.join(", ")}`, "warning");
    }
    isCreatingAlert = false;
    alertFormDirty = false;
    selectedAlertId = data.saved_id || payload.alert_rule.id || selectedAlertId;
    // Refresh the in-memory catalog from the save response WITHOUT re-rendering
    // the editor — re-rendering mid-edit would lose focus and feel like nothing
    // saved. A full render only happens on explicit (non-silent) saves.
    if (latestReport && Array.isArray(data.alert_rules)) {
      latestReport.alert_rules = data.alert_rules;
      if (data.host_catalog) latestReport.host_catalog = data.host_catalog;
    }
    flashSavedFields("saved");
    if (!silent) await loadStatus(true);
  } catch (error) {
    setSaveStatusText(`Error: ${error.message}`, "error");
    flashSavedFields("error");
  } finally {
    alertAutosaveInFlight = false;
  }
}

async function deleteAlert() {
  const selected = getSelectedAlert(latestReport);
  if (!selected) return;
  if (!confirm(`Delete alert "${selected.name}"? This cannot be undone.`)) return;
  try {
    const response = await fetch("/api/alert/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: selected.id, name: selected.name }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to delete alert");
    selectedAlertId = null;
    isCreatingAlert = false;
    await loadStatus();
  } catch (error) {
    alert(`Delete alert failed: ${error.message}`);
  }
}

async function rearmAlert() {
  const selected = getSelectedAlert(latestReport);
  if (!selected) {
    showToast("No alert selected to re-arm", "warning");
    return;
  }
  try {
    const response = await fetch("/api/alert/rearm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: selected.id, name: selected.name }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to rearm alert");
    const count = data.rearmed ?? 0;
    if (count > 0) {
      setSaveStatusText("Re-armed", "saved");
      showToast(data.message || `Re-armed ${count} instance(s)`, "success");
    } else {
      showToast(data.message || "Nothing to re-arm — alert was not paused", "info");
    }
    await loadStatus(true);
  } catch (error) {
    showToast(`Re-arm failed: ${error.message}`, "error");
  }
}

function startNewAlert() {
  isCreatingAlert = true;
  selectedAlertId = null;
  activeTab = "triggers";
  syncRoute();
  renderTabs();
  populateBlankEditor();
  setSaveStatusText("Draft incomplete: name + at least 1 target", "warning");
}

function populateBlankEditor() {
  const firstHost = Object.keys(latestReport?.host_catalog || {})[0];
  const blank = {
    id: "",
    name: "",
    description: "",
    type: "ssh",
    schedule: "*/30 * * * *",
    severity: "info",
    timeout: 30,
    notifications: true,
    command: "",
    url: "",
    query: "",
    threshold: "",
    threshold_query: "",
    comparator: "",
    accept_codes: [],
    ignore_targets: [],
    expect_empty: false,
    expect_nonempty: false,
    parse_cert_days: false,
    cert_warn_days: "",
    steps: [],
    fix_prompt: "",
    targets: firstHost ? [firstHost] : [],
    allowed_agents: [],
    custom_agents: [],
    emergency_actions: [],
    pause_schedule_on_fix_failed: true,
    token_protection: { enabled: true, max_prompt_tokens: 4000, max_response_tokens: 4000, max_total_tokens_per_run: 12000, notify_on_stop: true },
  };
  const fakeAlert = { id: "", name: "", description: "", targets: blank.targets, checks: [], config: blank };
  renderEditor(fakeAlert);
  if (latestReport) renderTargetChoices(fakeAlert, latestReport);
  attachAlertAutosaveListeners();
}

function renderTabs() {
  const checksPages = new Set(["alert", "host", "search"]);
  document.querySelectorAll(".nav-button").forEach((node) => {
    const page = node.dataset.page;
    node.classList.toggle("is-active", page === activePage || (page === "alert" && checksPages.has(activePage)));
  });
  // The 5 legacy check subtabs are consolidated into 2: "status" and "config".
  // "config" stacks the triggers/actions/targets/rules panels together.
  const configPanels = new Set(["triggers", "actions", "targets", "rules"]);
  const tabGroup = configPanels.has(activeTab) ? "config" : activeTab;
  document.querySelectorAll(".tab-button[data-tab]").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.tab === tabGroup);
  });
  document.querySelectorAll(".tab-panel").forEach((node) => {
    const panel = node.dataset.panel;
    const show = panel === activeTab || (tabGroup === "config" && configPanels.has(panel));
    node.classList.toggle("is-active", show);
  });
  document.querySelectorAll("[data-settings-tab]").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.settingsTab === activeSettingsTab);
  });
  document.querySelectorAll(".settings-tab-panel").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.settingsPanel === activeSettingsTab);
  });
}

function renderPageShell() {
  const meta = document.querySelector("#workspace-meta");
  if (meta && activePage !== "home") meta.textContent = "";
  // Full-width document pages hide the sidebar; detail pages keep it.
  const detailPages = new Set(["alert", "host"]);
  document.querySelector(".app-shell")?.classList.toggle("hide-sidebar", !detailPages.has(activePage));
  homeView.classList.toggle("is-active", activePage === "home");
  const rulesView = document.querySelector("#rules-view");
  if (rulesView) rulesView.classList.toggle("is-active", activePage === "rules");
  activityView.classList.toggle("is-active", activePage === "activity");
  hostView.classList.toggle("is-active", activePage === "host");
  searchView.classList.toggle("is-active", activePage === "search");
  settingsView.classList.toggle("is-active", activePage === "settings");
  if (alertmanagerView) alertmanagerView.classList.toggle("is-active", activePage === "alertmanager");
  if (metricsView) metricsView.classList.toggle("is-active", activePage === "metrics");
  if (activePage === "metrics") renderMetricsView();
  alertView.classList.toggle("is-active", activePage === "alert");
  alertSideColumn.style.display = activePage === "alert" ? "grid" : "none";
  document.querySelector(".workspace-grid").classList.toggle("single-column", activePage !== "alert");
  const checkSubtabs = document.querySelector("#check-subtabs");
  if (checkSubtabs) checkSubtabs.style.display = activePage === "alert" ? "flex" : "none";
  const settingsSubtabs = document.querySelector("#settings-subtabs");
  if (settingsSubtabs) settingsSubtabs.style.display = activePage === "settings" ? "flex" : "none";
  notificationsPopup.classList.toggle("is-open", notificationsOpen);
}

async function loadMobileAdminOverview() {
  const response = await fetch("/api/mobile/admin/overview", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to load mobile settings");
  mobileAdminOverview = data;
  return data;
}

async function saveMobileEndpointSettings() {
  mobileEndpointSaveStatus.textContent = "Saving...";
  const response = await fetch("/api/mobile/admin/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      public_scheme: mobilePublicScheme.value,
      public_hostname: mobilePublicHostname.value.trim(),
      public_port: Number(mobilePublicPort.value || 0),
      serve_host: mobileServeHost.value.trim(),
      serve_port: Number(mobileServePort.value || 0),
      tls_enabled: mobileTlsEnabled.checked,
      tls_certfile: mobileTlsCertfile.value.trim(),
      tls_keyfile: mobileTlsKeyfile.value.trim(),
    }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to save mobile endpoint settings");
  mobileAdminOverview = data;
  renderSettingsView();
}

async function createApiKey() {
  const scopes = [...apiKeyScopes.querySelectorAll("input:checked")].map((node) => node.value);
  if (!apiKeyName.value.trim()) {
    apiKeyCreateStatus.textContent = "Name is required";
    return;
  }
  apiKeyCreateStatus.textContent = "Generating...";
  const response = await fetch("/api/mobile/admin/api-keys/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: apiKeyName.value.trim(),
      notes: apiKeyNotes.value.trim(),
      device_limit: Number(apiKeyDeviceLimit.value || 3),
      allowed_targets: apiKeyAllowedTargets.value.trim(),
      scopes,
    }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to create api key");
  mobileAdminOverview = {
    ...(mobileAdminOverview || {}),
    api_keys: data.api_keys || [],
    devices: data.devices || [],
    mobile: mobileAdminOverview?.mobile || {},
  };
  apiKeyCreatedPanel.style.display = "block";
  apiKeyCreatedValue.textContent = data.raw_key || "";
  apiKeyCreateStatus.textContent = "API key created. Store it now: only shown once.";
  apiKeyForm.reset();
  apiKeyDeviceLimit.value = "3";
  apiKeyAllowedTargets.value = "";
  apiKeyScopes.querySelectorAll("input").forEach((node) => {
    node.checked = true;
  });
  renderSettingsView();
}

async function revokeApiKey(keyId) {
  const response = await fetch("/api/mobile/admin/api-keys/revoke", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: keyId }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to revoke api key");
  mobileAdminOverview = {
    ...(mobileAdminOverview || {}),
    api_keys: data.api_keys || [],
    devices: data.devices || [],
    mobile: mobileAdminOverview?.mobile || {},
  };
  renderSettingsView();
}

async function revokeMobileDevice(deviceId) {
  const response = await fetch("/api/mobile/admin/devices/revoke", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: deviceId }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "failed to revoke device");
  mobileAdminOverview = {
    ...(mobileAdminOverview || {}),
    api_keys: data.api_keys || [],
    devices: data.devices || [],
    mobile: mobileAdminOverview?.mobile || {},
  };
  renderSettingsView();
}

function applyEngineMode(report) {
  const orchestrator = report.native_engine_enabled === false;
  document.body.classList.toggle("orchestrator-mode", orchestrator);
  // Sidebar label reflects what the left rail now lists.
  const sidebarLabel = document.querySelector(".sidebar-label");
  if (sidebarLabel) sidebarLabel.textContent = orchestrator ? "Problems" : "Checks";
  // Hide the native "Checks" nav and the "+ add check" button when checks are
  // no longer RootCause's source of truth.
  const checksNav = document.querySelector('.nav-button[data-page="alert"]');
  if (checksNav) checksNav.style.display = orchestrator ? "none" : "";
  if (newAlertButton) newAlertButton.style.display = orchestrator ? "none" : "";
  // Hide the Dashboard's native "Current Alerts" table (driven by native checks).
  const nativeAlertsTable = dashboardAlertsTable ? dashboardAlertsTable.closest(".table-panel") : null;
  if (nativeAlertsTable) nativeAlertsTable.style.display = orchestrator ? "none" : "";
}

function render(report) {
  if (report.error) {
    summaryCards.innerHTML = `<div class="empty">${report.error}</div>`;
    alertList.innerHTML = '<div class="empty">No alerts available.</div>';
    return;
  }

  latestReport = report;
  globalSearchInput.value = currentSearchQuery;
  applyEngineMode(report);
  renderHostsEditor(report);
  renderAlertList(report);
  renderNotifications(report);
  renderPageShell();

  if (activePage === "home") {
    workspaceTitle.textContent = "Problems";
    const counts = problemSeverityCounts();
    headerStatus.innerHTML =
      `<span class="sev-summary sev-summary-critical">${counts.critical} Critical</span>` +
      `<span class="sev-summary sev-summary-high">${counts.high} High</span>` +
      `<span class="sev-summary sev-summary-warning">${counts.warning} Warning</span>`;
    const meta = document.querySelector("#workspace-meta");
    if (meta) meta.textContent = latestProblems.length ? "Last updated: just now" : "";
    renderTabs();
    renderProblems();
    return;
  }

  if (activePage === "rules") {
    workspaceTitle.textContent = "Rules";
    headerStatus.textContent = "Datasource-triggered remediation";
    renderTabs();
    renderRulesPage(report);
    return;
  }

  if (activePage === "host") {
    workspaceTitle.textContent = selectedHostName ? `Host · ${selectedHostName}` : "Host";
    headerStatus.textContent = selectedHostName || "";
    renderHostView(report);
    return;
  }

  if (activePage === "activity") {
    workspaceTitle.textContent = "Activity";
    headerStatus.textContent = "Recent runs and execution history";
    renderTabs();
    renderActivityView(report);
    return;
  }

  if (activePage === "search") {
    workspaceTitle.textContent = "Search";
    headerStatus.textContent = currentSearchQuery ? `Query: ${currentSearchQuery}` : "";
    renderTabs();
    renderSearchResults(report);
    return;
  }

  if (activePage === "settings") {
    workspaceTitle.textContent = "Settings";
    headerStatus.textContent = "Mobile, maintenance and API keys";
    renderTabs();
    renderSettingsView();
    return;
  }

  if (activePage === "metrics") {
    workspaceTitle.textContent = "Observability";
    headerStatus.textContent = "Grafana dashboards · system, GPU, containers and RootCause metrics";
    renderTabs();
    renderMetricsView();
    return;
  }

  if (activePage === "alertmanager") {
    workspaceTitle.textContent = "Alertmanager";
    headerStatus.textContent = "Import alerts as RootCause checks";
    renderTabs();
    if (alertmanagerData) {
      renderAlertmanagerView(alertmanagerData);
    } else if (alertmanagerSourcesList) {
      alertmanagerSourcesList.innerHTML = `<div class="empty" style="padding:24px;text-align:center;color:var(--muted)">Loading…</div>`;
    }
    return;
  }

  if (isCreatingAlert) {
    workspaceTitle.textContent = "New alert";
    headerStatus.textContent = "";
    renderTabs();
    populateBlankEditor();
    return;
  }

  const selected = getSelectedAlert(report);
  if (!selected) {
    workspaceTitle.textContent = "RootCause";
    headerStatus.textContent = "";
    renderTabs();
    return;
  }

  workspaceTitle.textContent = selected.name;
  headerStatus.textContent = selected.isPaused ? "Paused" : selected.statusText;
  syncRoute(false);

  const entries = getHistoryForAlert(report, selected.name);
  renderSummary(report, selected, entries);
  renderCheckGrafanaPanels(selected);
  renderExecutions(selected, entries);
  renderHostsPreview(selected, report);
  renderEditor(selected);
  renderTargetChoices(selected, report);
  renderPreviewSection(selected, report);
  attachAlertAutosaveListeners();
  renderTabs();
}

let latestProblems = [];
let problemSevFilter = "all";
let problemPage = 1;
let problemPageSize = 25;
const expandedProblems = new Set();

function formatDuration(fromIso) {
  if (!fromIso) return "—";
  const secs = Math.max(0, Math.round((Date.now() - new Date(fromIso).getTime()) / 1000));
  if (secs < 60) return `${secs}s`;
  if (secs < 3600) return `${Math.floor(secs / 60)}m`;
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ${Math.floor((secs % 3600) / 60)}m`;
  return `${Math.floor(secs / 86400)}d ${Math.floor((secs % 86400) / 3600)}h`;
}

const SEV_CARD_DEFS = [
  ["critical", "Critical"],
  ["high", "High"],
  ["warning", "Warning"],
];

// Build a small SVG sparkline from the number of problems of `sev` that
// started in each of the last 24 hourly buckets. It's a lightweight but real
// signal (not a placeholder) — a flat baseline when nothing started recently.
function severitySparkline(sev) {
  const buckets = new Array(24).fill(0);
  const now = Date.now();
  latestProblems.forEach((p) => {
    if ((p.severity || "") !== sev) return;
    const started = p.started_at || p.first_seen;
    if (!started) return;
    const hoursAgo = Math.floor((now - new Date(started).getTime()) / 3600000);
    if (hoursAgo >= 0 && hoursAgo < 24) buckets[23 - hoursAgo] += 1;
  });
  const max = Math.max(1, ...buckets);
  const w = 86;
  const h = 30;
  const step = w / (buckets.length - 1);
  const points = buckets
    .map((v, i) => `${(i * step).toFixed(1)},${(h - 2 - (v / max) * (h - 4)).toFixed(1)}`)
    .join(" ");
  return `<svg class="sev-sparkline sev-spark-${sev}" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true"><polyline points="${points}"/></svg>`;
}

function severityCardIcon(sev) {
  if (sev === "critical")
    return `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6" stroke-linecap="round"/></svg>`;
  if (sev === "high")
    return `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9"/><path d="M12 7v6" stroke-linecap="round"/><circle cx="12" cy="16.5" r="0.6" fill="currentColor" stroke="none"/></svg>`;
  return `<svg viewBox="0 0 24 24" fill="none"><path d="M12 4l8 14H4z" stroke-linejoin="round"/><path d="M12 10v4" stroke-linecap="round"/><circle cx="12" cy="16.5" r="0.6" fill="currentColor" stroke="none"/></svg>`;
}

function renderSeverityCards() {
  const wrap = document.querySelector("#sev-summary-cards");
  if (!wrap) return;
  const counts = problemSeverityCounts();
  wrap.innerHTML = SEV_CARD_DEFS.map(
    ([sev, label]) => `<button class="sev-summary-card sev-card-${sev} ${problemSevFilter === sev ? "is-active" : ""}" type="button" data-sevcard="${sev}">
      <span class="sev-card-icon">${severityCardIcon(sev)}</span>
      <span class="sev-card-body">
        <span class="sev-card-label">${label}</span>
        <span class="sev-card-count">${counts[sev] || 0}</span>
      </span>
      <span class="sev-card-spark">${severitySparkline(sev)}<span class="sev-card-spark-label">Last 24h</span></span>
    </button>`,
  ).join("");
  wrap.querySelectorAll("[data-sevcard]").forEach((node) =>
    node.addEventListener("click", () => {
      const next = node.dataset.sevcard;
      problemSevFilter = problemSevFilter === next ? "all" : next;
      problemPage = 1;
      renderProblems();
    }),
  );
}

function renderProblems() {
  if (!problemsTable) return;
  renderSeverityCards();
  const counts = problemSeverityCounts();
  const filters = document.querySelector("#problems-sev-filters");
  if (filters) {
    const defs = [["all", "All", latestProblems.length], ["critical", "Critical", counts.critical], ["high", "High", counts.high], ["warning", "Warning", counts.warning]];
    filters.innerHTML = defs
      .map(([k, label, n]) => `<button class="problems-tab ${problemSevFilter === k ? "is-active" : ""} pt-${k}" type="button" data-sevfilter="${k}">${label} <span class="problems-tab-count">(${n})</span></button>`)
      .join("");
    filters.querySelectorAll("[data-sevfilter]").forEach((node) => {
      node.addEventListener("click", () => {
        problemSevFilter = node.dataset.sevfilter;
        problemPage = 1;
        renderProblems();
      });
    });
  }
  const problems = latestProblems.filter((p) => problemSevFilter === "all" || (p.severity || "") === problemSevFilter);
  if (problemsCount) problemsCount.textContent = `${problems.length} problem${problems.length === 1 ? "" : "s"}`;
  const footer = document.querySelector("#problems-footer");
  if (!problems.length) {
    problemsTable.innerHTML = `<tr><td colspan="8" class="empty">No active problems.</td></tr>`;
    if (footer) footer.innerHTML = "";
    return;
  }
  const pageCount = Math.max(1, Math.ceil(problems.length / problemPageSize));
  if (problemPage > pageCount) problemPage = pageCount;
  const start = (problemPage - 1) * problemPageSize;
  const pageItems = problems.slice(start, start + problemPageSize);
  problemsTable.innerHTML = pageItems
    .map((p) => {
      const sev = String(p.severity || "unknown");
      const started = p.started_at || p.first_seen;
      const silencedBadge = p.silenced ? ` <span class="mini-badge warn">SILENCED</span>` : "";
      const link = p.source_url ? `<a class="row-action" href="${escapeAttr(p.source_url)}" target="_blank" rel="noopener">View</a>` : "";
      const ackButton = p.acknowledged
        ? `<span class="mini-badge ok">ACK</span>`
        : `<button class="row-action ghost-action" type="button" data-problem-ack="${escapeAttr(p.key)}">Ack</button>`;
      const nComments = (p.comments || []).length;
      const commentBtn = `<button class="row-action ghost-action" type="button" data-problem-toggle="${escapeAttr(p.key)}">Comment${nComments ? ` (${nComments})` : ""}</button>`;
      const source = String(p.source || "?");
      const sourceLabel = source.charAt(0).toUpperCase() + source.slice(1);
      let row = `<tr class="problem-row" data-sev="${escapeAttr(sev)}">
        <td><span class="sev-cell"><span class="sev-dot sev-dot-${escapeAttr(sev)}"></span><span class="sev-badge sev-${escapeAttr(sev)}">${escapeHtml(sev.toUpperCase())}</span></span></td>
        <td class="nowrap">${escapeHtml(formatDateShort(started))}</td>
        <td>${escapeHtml(p.host || "—")}</td>
        <td><div class="problem-name">${escapeHtml(p.name || "unnamed")}${silencedBadge}</div>
            <div class="problem-summary">${escapeHtml(p.summary || p.description || "")}</div></td>
        <td><span class="source-badge">${escapeHtml(sourceLabel)}</span></td>
        <td class="nowrap">${escapeHtml(formatDuration(started))}</td>
        <td>${ackButton}</td>
        <td class="row-actions">${commentBtn}${link}</td>
      </tr>`;
      if (expandedProblems.has(p.key)) {
        const comments = (p.comments || [])
          .map((c) => `<div class="problem-comment"><span class="problem-comment-meta">${escapeHtml(c.by || "?")} · ${escapeHtml(formatRelativeTime(c.at))}</span><span>${escapeHtml(c.text)}</span></div>`)
          .join("") || `<div class="problem-comment-empty">No comments yet.</div>`;
        row += `<tr class="problem-comment-row"><td colspan="8">
          <div class="problem-comments">${comments}</div>
          <form class="problem-comment-form" data-problem-comment="${escapeAttr(p.key)}">
            <input type="text" placeholder="Add a comment…" required>
            <button class="row-action" type="submit">Send</button>
          </form>
        </td></tr>`;
      }
      return row;
    })
    .join("");
  if (footer) {
    const from = start + 1;
    const to = Math.min(start + problemPageSize, problems.length);
    footer.innerHTML = `
      <span class="problems-footer-count">Showing ${from} to ${to} of ${problems.length} problems</span>
      <div class="problems-pager">
        <button class="pager-button" type="button" data-page-prev ${problemPage <= 1 ? "disabled" : ""}>&#8249;</button>
        <span class="pager-current">${problemPage}</span>
        <button class="pager-button" type="button" data-page-next ${problemPage >= pageCount ? "disabled" : ""}>&#8250;</button>
        <select class="pager-size" data-page-size aria-label="Page size">
          ${[10, 25, 50, 100].map((n) => `<option value="${n}" ${n === problemPageSize ? "selected" : ""}>${n} / page</option>`).join("")}
        </select>
      </div>`;
    footer.querySelector("[data-page-prev]")?.addEventListener("click", () => {
      if (problemPage > 1) { problemPage -= 1; renderProblems(); }
    });
    footer.querySelector("[data-page-next]")?.addEventListener("click", () => {
      if (problemPage < pageCount) { problemPage += 1; renderProblems(); }
    });
    footer.querySelector("[data-page-size]")?.addEventListener("change", (e) => {
      problemPageSize = Number(e.target.value) || 25;
      problemPage = 1;
      renderProblems();
    });
  }
}

function formatDateShort(value) {
  if (!value) return "—";
  const d = new Date(value);
  return d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

async function fetchProblems() {
  try {
    const response = await fetch("/api/problems", { cache: "no-store" });
    const data = await response.json();
    latestProblems = data.problems || [];
  } catch (error) {
    latestProblems = [];
  }
  return latestProblems;
}

async function loadProblems() {
  await fetchProblems();
  renderProblems();
  if (latestReport && latestReport.native_engine_enabled === false) renderSidebarProblems();
}

function problemSeverityCounts() {
  return latestProblems.reduce(
    (acc, p) => {
      const s = p.severity || "unknown";
      if (s === "critical") acc.critical += 1;
      else if (s === "high") acc.high += 1;
      else acc.warning += 1;
      return acc;
    },
    { critical: 0, high: 0, warning: 0 },
  );
}

function renderSidebarProblems() {
  const query = alertSearch.value.trim().toLowerCase();
  const problems = latestProblems.filter((p) => {
    if (sidebarStateFilter !== "all" && (p.severity || "") !== sidebarStateFilter) return false;
    if (!query) return true;
    return `${p.name} ${p.summary} ${p.host} ${p.source}`.toLowerCase().includes(query);
  });
  const counts = problemSeverityCounts();
  sidebarOverview.innerHTML = `
    <button class="overview-pill bad ${sidebarStateFilter === "critical" ? "is-active" : ""}" data-filter="critical" type="button">${counts.critical} critical</button>
    <button class="overview-pill warn ${sidebarStateFilter === "high" ? "is-active" : ""}" data-filter="high" type="button">${counts.high} high</button>
    <button class="overview-pill ok ${sidebarStateFilter === "warning" ? "is-active" : ""}" data-filter="warning" type="button">${counts.warning} warning</button>
  `;
  sidebarOverview.querySelectorAll("[data-filter]").forEach((node) => {
    node.addEventListener("click", () => {
      const next = node.dataset.filter;
      sidebarStateFilter = sidebarStateFilter === next ? "all" : next;
      renderSidebarProblems();
    });
  });
  if (!problems.length) {
    alertList.innerHTML = '<div class="empty">No active problems.</div>';
    return;
  }
  alertList.innerHTML = problems
    .map(
      (p) => `<button class="sidebar-problem" type="button" data-problem-nav="1">
        <span class="sidebar-problem-dot sev-dot-${escapeAttr(p.severity || "unknown")}"></span>
        <span class="sidebar-problem-body">
          <span class="sidebar-problem-name">${escapeHtml(p.name || "unnamed")}</span>
          <span class="sidebar-problem-meta">${escapeHtml(p.source || "?")} · ${escapeHtml(p.host || "—")}</span>
        </span>
      </button>`,
    )
    .join("");
  alertList.querySelectorAll("[data-problem-nav]").forEach((node) => {
    node.addEventListener("click", () => {
      activePage = "home";
      syncRoute();
      if (latestReport) render(latestReport);
    });
  });
}

async function postProblemAction(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (response.ok) {
    latestProblems = data.problems || [];
    renderProblems();
  }
  return data;
}

document.querySelector("#problems-show-filters")?.addEventListener("click", (event) => {
  const btn = event.currentTarget;
  const tabs = document.querySelector("#problems-sev-filters");
  const hidden = tabs.classList.toggle("is-collapsed");
  btn.setAttribute("aria-expanded", String(!hidden));
});

if (problemsTable) {
  problemsTable.addEventListener("click", async (event) => {
    const toggle = event.target.closest("[data-problem-toggle]");
    if (toggle) {
      const key = toggle.dataset.problemToggle;
      if (expandedProblems.has(key)) expandedProblems.delete(key);
      else expandedProblems.add(key);
      renderProblems();
      return;
    }
    const ack = event.target.closest("[data-problem-ack]");
    if (ack) {
      ack.disabled = true;
      await postProblemAction("/api/problems/ack", { key: ack.dataset.problemAck });
    }
  });
  problemsTable.addEventListener("submit", async (event) => {
    const form = event.target.closest("[data-problem-comment]");
    if (!form) return;
    event.preventDefault();
    const input = form.querySelector("input");
    const text = input.value.trim();
    if (!text) return;
    await postProblemAction("/api/problems/comment", { key: form.dataset.problemComment, text });
  });
}

// ── Rules page ────────────────────────────────────────────────────────────
let ruleFormState = null; // null = list; object = editing/creating
let pendingRuleEdit = null; // {mode:"new"} | {mode:"edit",id} from the URL, resolved once the report loads
const SEVERITIES = ["critical", "high", "warning", "info"];

function blankRule() {
  return { name: "", enabled: true, trigger: "auto", datasource_ids: [], match: {}, actions: [] };
}
const ACTION_TYPES = ["ai_agent", "jira", "bash", "docker", "systemd", "notification", "http", "wait", "silence", "noop"];

async function postJson(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin" },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `request failed (${response.status})`);
  return data;
}

function renderRulesPage(report) {
  const list = document.querySelector("#rules-list");
  const listPanel = document.querySelector("#rules-list-panel");
  const formPanel = document.querySelector("#rule-form-panel");
  if (!list || !formPanel) return;
  // Resolve a shareable /rules/<id>/edit (or /rules/new) URL into editor state
  // once the report (with rules) is available.
  if (pendingRuleEdit && !ruleFormState) {
    if (pendingRuleEdit.mode === "new") {
      ruleFormState = blankRule();
      pendingRuleEdit = null;
    } else {
      const found = (report.rules || []).find((r) => r.id === pendingRuleEdit.id);
      if (found) { ruleFormState = JSON.parse(JSON.stringify(found)); pendingRuleEdit = null; }
      else if ((report.rules || []).length) { pendingRuleEdit = null; } // unknown id → show list
    }
  }
  if (ruleFormState) {
    listPanel.style.display = "none";
    formPanel.style.display = "";
    renderRuleForm(report);
    return;
  }
  formPanel.style.display = "none";
  listPanel.style.display = "";
  const rules = report.rules || [];
  const dsById = Object.fromEntries((report.datasources || []).map((d) => [d.id, d]));
  if (!rules.length) {
    list.innerHTML = `<div class="empty">No rules yet. Add one to react to problems from your datasources.</div>`;
    return;
  }
  list.innerHTML = rules
    .map((r) => {
      const dss = (r.datasource_ids || []).map((id) => dsById[id]?.name || id).join(", ") || "any datasource";
      const acts = (r.actions || []).map((a) => a.type).join(" → ") || "no actions";
      const off = r.enabled === false ? ' <span class="mini-badge warn">OFF</span>' : "";
      return `<div class="rule-card" data-rule-edit="${escapeAttr(r.id)}">
        <div class="rule-card-main">
          <div class="rule-card-name">${escapeHtml(r.name)}${off}</div>
          <div class="rule-card-meta">${escapeHtml(dss)} &nbsp;·&nbsp; ${escapeHtml(acts)}</div>
        </div>
        <button class="row-action" type="button" data-rule-del="${escapeAttr(r.id)}">Delete</button>
      </div>`;
    })
    .join("");
  list.querySelectorAll("[data-rule-edit]").forEach((node) =>
    node.addEventListener("click", (e) => {
      if (e.target.closest("[data-rule-del]")) return;
      const id = node.dataset.ruleEdit;
      ruleFormState = JSON.parse(JSON.stringify((report.rules || []).find((r) => r.id === id) || {}));
      syncRoute();
      render(latestReport);
    }),
  );
  list.querySelectorAll("[data-rule-del]").forEach((node) =>
    node.addEventListener("click", async (e) => {
      e.stopPropagation();
      if (!confirm("Delete this rule?")) return;
      await postJson("/api/rule/delete", { id: node.dataset.ruleDel });
      await loadStatus(true);
    }),
  );
}

const SEV_PILL_META = {
  critical: { label: "Critical", icon: `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6" stroke-linecap="round"/></svg>` },
  high: { label: "High", icon: `<svg viewBox="0 0 24 24" fill="none"><path d="M12 4l8 14H4z" stroke-linejoin="round"/><path d="M12 10v4" stroke-linecap="round"/></svg>` },
  warning: { label: "Warning", icon: `<svg viewBox="0 0 24 24" fill="none"><path d="M10.3 4.3l-7 12A2 2 0 0 0 5 19.5h14a2 2 0 0 0 1.7-3.2l-7-12a2 2 0 0 0-3.4 0z" stroke-linejoin="round"/><path d="M12 9v4" stroke-linecap="round"/></svg>` },
  info: { label: "Info", icon: `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9"/><path d="M12 11v5" stroke-linecap="round"/><circle cx="12" cy="8" r="0.6" fill="currentColor" stroke="none"/></svg>` },
};

let rulePromTimer = null;

function rulePromDatasource(report) {
  const sel = ruleFormState.datasource_ids || [];
  return (report.datasources || []).find((d) => sel.includes(d.id) && d.type === "prometheus") || null;
}

function renderRuleForm(report) {
  const r = ruleFormState;
  const datasources = report.datasources || [];
  const match = r.match || {};
  r.actions = r.actions || [];

  // A rule's datasources must all be the SAME type (you query one kind of
  // backend at a time), so once one is picked, other-type cards are locked.
  const selectedType = (() => {
    const first = (r.datasource_ids || [])[0];
    const d = datasources.find((x) => x.id === first);
    return d ? String(d.type) : null;
  })();
  const dsCards = datasources.length
    ? datasources
        .map((d) => {
          const sel = (r.datasource_ids || []).includes(d.id);
          const type = String(d.type || "prometheus");
          const locked = selectedType && type !== selectedType && !sel;
          const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
          const host = dsHostFromUrl(d.url) || d.name || typeLabel;
          const status = d.enabled === false
            ? `<span class="ds-status ds-status-off"><span class="ds-status-dot"></span>Disabled</span>`
            : `<span class="ds-status ds-status-on"><span class="ds-status-dot"></span>Connected</span>`;
          return `<button type="button" class="re-ds-card ${sel ? "is-selected" : ""} ${locked ? "is-locked" : ""}" data-ds-toggle="${escapeAttr(d.id)}" data-ds-type="${escapeAttr(type)}" ${locked ? "title='Pick datasources of a single type per rule'" : ""}>
            ${sel ? `<span class="re-ds-check">✓</span>` : ""}
            <span class="ds-card-icon ds-icon-${escapeAttr(type)}">${dsBrandIcon(type)}</span>
            <span class="re-ds-body">
              <span class="re-ds-title">${escapeHtml(typeLabel)} <span class="ds-card-sep">·</span> ${escapeHtml(host)}</span>
              <span class="ds-card-tags"><span class="ds-badge">${escapeHtml(typeLabel)}</span>${status}</span>
            </span>
          </button>`;
        })
        .join("")
    : `<p class="form-hint">No datasources yet — add one in Settings → Datasources.</p>`;

  const sevPills = SEVERITIES.map((s) => {
    const on = (match.severity || []).includes(s);
    return `<button type="button" class="re-sev-pill re-sev-${s} ${on ? "is-on" : ""}" data-sev-toggle="${s}">
      <span class="re-sev-icon">${SEV_PILL_META[s].icon}</span>${SEV_PILL_META[s].label}</button>`;
  }).join("");

  document.querySelector("#rule-form-title").textContent = r.id ? "Edit rule" : "Add rule";
  document.querySelector("#rule-form-body").innerHTML = `
    <div class="rule-editor">
      <section class="editor-card">
        <div class="editor-card-head">
          <span class="editor-card-icon">${ICON_DOC}</span>
          <div><h3>Rule basics</h3><p>Define the basic information and trigger type for this rule.</p></div>
        </div>
        <div class="editor-card-body">
          <div class="re-grid re-grid-basics">
            <label class="re-field"><span>Rule name</span><input id="rule-f-name" type="text" value="${escapeAttr(r.name || "")}" placeholder="e.g. disk_root"></label>
            <div class="re-field"><span>Enabled</span>
              <label class="re-toggle"><input type="checkbox" id="rule-f-enabled" ${r.enabled !== false ? "checked" : ""}><span class="re-toggle-track"></span></label>
            </div>
            <label class="re-field"><span>Trigger type</span><select id="rule-f-trigger">
              <option value="auto" ${(r.trigger || "auto") === "auto" ? "selected" : ""}>Datasource trigger</option>
              <option value="webhook" ${r.trigger === "webhook" ? "selected" : ""}>Webhook (push)</option>
              <option value="polling" ${r.trigger === "polling" ? "selected" : ""}>Polling (pull)</option>
            </select></label>
          </div>
        </div>
      </section>

      <section class="editor-card">
        <div class="editor-card-head">
          <span class="editor-card-icon">${ICON_BOLT}</span>
          <div><h3>Trigger</h3><p>Choose the datasource and define when this rule should fire.</p></div>
        </div>
        <div class="editor-card-body">
          <div class="re-trigger-grid">
            <div class="re-trigger-left">
              <span class="re-label">Datasources</span>
              <div class="re-ds-cards" id="rule-ds-cards">${dsCards}</div>
              <span class="re-label">Match conditions</span>
              <div class="re-sev-pills" id="rule-sev-pills">${sevPills}</div>
              <div class="re-grid re-grid-2">
                <label class="re-field"><span>Problem name pattern</span><input id="rule-f-namerx" type="text" value="${escapeAttr(match.name_regex || "")}" placeholder="e.g. Disk.*"></label>
                <label class="re-field"><span>Host filter</span><input id="rule-f-host" type="text" value="${escapeAttr((match.host || []).join(", "))}" placeholder="e.g. mediaserver"></label>
              </div>
            </div>
            <div class="re-trigger-right" id="rule-preview-wrap"></div>
          </div>
        </div>
      </section>

      <section class="editor-card">
        <div class="editor-card-head">
          <span class="editor-card-icon">${ICON_WAND}</span>
          <div><h3>Actions</h3><p>What should happen when this rule fires?</p></div>
        </div>
        <div class="editor-card-body">
          <div id="rule-actions-list"></div>
          <button class="re-add-action" id="rule-action-add" type="button">+ Add action</button>
        </div>
      </section>
      <p class="caption" id="rule-save-status"></p>
    </div>`;

  renderRuleActions();
  renderRulePreview(report);

  document.querySelector("#rule-ds-cards").addEventListener("click", (e) => {
    const card = e.target.closest("[data-ds-toggle]");
    if (!card || card.classList.contains("is-locked")) return; // single-type rule
    syncRuleFormFromDom();
    const id = card.dataset.dsToggle;
    const set = new Set(ruleFormState.datasource_ids || []);
    set.has(id) ? set.delete(id) : set.add(id);
    ruleFormState.datasource_ids = [...set];
    renderRuleForm(report);
  });
  document.querySelector("#rule-sev-pills").addEventListener("click", (e) => {
    const pill = e.target.closest("[data-sev-toggle]");
    if (!pill) return;
    syncRuleFormFromDom();
    const s = pill.dataset.sevToggle;
    const set = new Set((ruleFormState.match && ruleFormState.match.severity) || []);
    set.has(s) ? set.delete(s) : set.add(s);
    ruleFormState.match = { ...(ruleFormState.match || {}) };
    if (set.size) ruleFormState.match.severity = [...set];
    else delete ruleFormState.match.severity;
    renderRuleForm(report);
  });
  document.querySelector("#rule-action-add").addEventListener("click", () => {
    syncRuleFormFromDom();
    ruleFormState.actions.push({ type: "ai_agent", when: "on_alert" });
    renderRuleForm(report);
  });
}

// Embedded Prometheus preview — lets the author validate a metric + threshold
// while building the rule, and links out to the datasource for deeper work.
function renderRulePreview(report) {
  const wrap = document.querySelector("#rule-preview-wrap");
  if (!wrap) return;
  const ds = rulePromDatasource(report);
  if (!ds) {
    wrap.innerHTML = `<div class="re-preview-empty">${ICON_CHART}<p>Select a Prometheus datasource to preview a metric and threshold here.</p></div>`;
    return;
  }
  const q = ruleFormState.preview_query || "";
  const openUrl = ds.url ? `${ds.url.replace(/\/$/, "")}/graph?g0.expr=${encodeURIComponent(q || "")}&g0.tab=0` : "#";
  wrap.innerHTML = `
    <div class="re-preview-head">
      <span class="re-label">Preview</span>
      <a class="re-preview-open" href="${escapeAttr(openUrl)}" target="_blank" rel="noopener">Open in ${escapeHtml(ds.name || "Prometheus")} ↗</a>
    </div>
    <input class="re-preview-query" id="rule-preview-query" type="text" value="${escapeAttr(q)}" placeholder='PromQL with threshold, e.g. node_load5 > 10'>
    <div class="re-preview-toolbar">
      <select id="rule-preview-range">
        <option value="15">15m</option><option value="60" selected>1h</option>
        <option value="360">6h</option><option value="1440">24h</option>
      </select>
      <span class="re-preview-status" id="rule-preview-status"></span>
    </div>
    <div class="re-preview-chart" id="rule-preview-chart"><div class="prom-empty">Type a PromQL expression to preview…</div></div>`;
  const input = document.querySelector("#rule-preview-query");
  const trigger = () => { clearTimeout(rulePromTimer); rulePromTimer = setTimeout(() => refreshRulePromPreview(ds), 450); };
  input.addEventListener("input", () => { ruleFormState.preview_query = input.value; trigger(); });
  document.querySelector("#rule-preview-range").addEventListener("change", () => refreshRulePromPreview(ds));
  if (q) refreshRulePromPreview(ds);
}

async function refreshRulePromPreview(ds) {
  const chart = document.querySelector("#rule-preview-chart");
  const statusEl = document.querySelector("#rule-preview-status");
  if (!chart) return;
  const query = (document.querySelector("#rule-preview-query")?.value || "").trim();
  if (!query) { chart.innerHTML = '<div class="prom-empty">Type a PromQL expression to preview…</div>'; if (statusEl) statusEl.textContent = ""; return; }
  const { metric, threshold } = parsePromExpr(query);
  const minutes = document.querySelector("#rule-preview-range")?.value || "60";
  if (statusEl) statusEl.textContent = "…";
  try {
    const params = new URLSearchParams({ query: metric || query, expr: query, minutes, ds: ds.id });
    const resp = await fetch(`/api/prom_range?${params.toString()}`);
    const data = await resp.json();
    if (!data.ok) { chart.innerHTML = `<div class="prom-empty">${escapeHtml(data.error || "error")}</div>`; if (statusEl) statusEl.textContent = ""; return; }
    const series = (data.data && data.data.result) || [];
    drawPromChart(chart, series, threshold, data.start, data.end);
    if (statusEl && typeof data.firing === "boolean") {
      statusEl.textContent = data.firing ? "● Above threshold" : "● Within range";
      statusEl.className = data.firing ? "re-preview-status fire" : "re-preview-status ok";
    } else if (statusEl) {
      statusEl.textContent = "";
    }
  } catch (err) {
    chart.innerHTML = `<div class="prom-empty">${escapeHtml(err.message)}</div>`;
    if (statusEl) statusEl.textContent = "";
  }
}

const ACTION_TYPE_LABELS = {
  ai_agent: "ai_agent", jira: "Send to Jira", bash: "bash", docker: "docker", systemd: "systemd",
  notification: "notification", http: "http", wait: "wait", silence: "silence", noop: "noop",
};

function actionFields(a, i) {
  const t = a.type;
  if (t === "ai_agent")
    return `<label class="re-field re-field-grow"><span>Fix prompt</span><textarea class="re-fix-prompt" data-af="fix_prompt" data-ai="${i}" rows="5" placeholder="Goal: restore the service with the smallest, safest change possible…">${escapeHtml(a.fix_prompt || "")}</textarea></label>`;
  if (t === "jira")
    return `<div class="re-field re-field-grow re-jira-note">${ICON_JIRA}<span>Creates / reuses a Jira ticket for the matched problem using <strong>Settings ▸ Webhooks ▸ Jira</strong>. Comments and resolution sync automatically.</span></div>
      <label class="re-field"><span>Comment (optional)</span><input type="text" data-af="message" data-ai="${i}" value="${escapeAttr(a.message || "")}" placeholder="{name} fired on {target}"></label>`;
  if (t === "bash")
    return `<label class="re-field re-field-grow"><span>Command</span><input type="text" data-af="command" data-ai="${i}" value="${escapeAttr(a.command || "")}"></label>
      <label class="re-field"><span>Run on</span><select data-af="run_on" data-ai="${i}"><option value="local" ${a.run_on === "local" ? "selected" : ""}>local</option><option value="ssh" ${a.run_on === "ssh" ? "selected" : ""}>ssh (host)</option></select></label>`;
  if (t === "docker")
    return `<label class="re-field re-field-grow"><span>Container</span><input type="text" data-af="name" data-ai="${i}" value="${escapeAttr(a.name || "")}"></label>
      <label class="re-field"><span>Action</span><select data-af="action" data-ai="${i}">${["restart", "start", "stop", "reload"].map((v) => `<option ${a.action === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>`;
  if (t === "systemd")
    return `<label class="re-field re-field-grow"><span>Unit</span><input type="text" data-af="unit" data-ai="${i}" value="${escapeAttr(a.unit || "")}"></label>
      <label class="re-field"><span>Action</span><select data-af="action" data-ai="${i}">${["restart", "start", "stop", "reload"].map((v) => `<option ${a.action === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>`;
  if (t === "notification")
    return `<label class="re-field re-field-grow"><span>Channels</span><input type="text" data-af="channels_csv" data-ai="${i}" value="${escapeAttr((a.channels || ["email"]).join(", "))}" placeholder="email, push"></label>`;
  if (t === "http")
    return `<label class="re-field re-field-grow"><span>URL</span><input type="text" data-af="url" data-ai="${i}" value="${escapeAttr(a.url || "")}"></label>
      <label class="re-field"><span>Method</span><input type="text" data-af="method" data-ai="${i}" value="${escapeAttr(a.method || "POST")}"></label>`;
  if (t === "wait")
    return `<label class="re-field"><span>Seconds</span><input type="number" data-af="seconds" data-ai="${i}" value="${escapeAttr(a.seconds || 5)}"></label>`;
  if (t === "silence")
    return `<label class="re-field"><span>Minutes</span><input type="number" data-af="minutes" data-ai="${i}" value="${escapeAttr(a.minutes || 30)}"></label>`;
  return `<p class="form-hint re-field-grow">No extra configuration for this action.</p>`;
}

function renderRuleActions() {
  const wrap = document.querySelector("#rule-actions-list");
  if (!wrap) return;
  const actions = ruleFormState.actions || [];
  if (!actions.length) {
    wrap.innerHTML = `<p class="form-hint">No actions yet — the rule will only surface the problem. Add an action below.</p>`;
    return;
  }
  wrap.innerHTML = actions
    .map(
      (a, i) => `<div class="re-action-row">
      <select class="re-action-type" data-action-type="${i}">${ACTION_TYPES.map((t) => `<option value="${t}" ${a.type === t ? "selected" : ""}>${ACTION_TYPE_LABELS[t] || t}</option>`).join("")}</select>
      <div class="re-action-fields">${actionFields(a, i)}</div>
      <button class="re-action-del" type="button" data-action-del="${i}" aria-label="Remove action">${ICON_TRASH}</button>
    </div>`,
    )
    .join("");
  wrap.querySelectorAll("[data-action-type]").forEach((node) =>
    node.addEventListener("change", () => {
      syncRuleFormFromDom();
      ruleFormState.actions[Number(node.dataset.actionType)] = { type: node.value, when: "on_alert" };
      renderRuleActions();
    }),
  );
  wrap.querySelectorAll("[data-action-del]").forEach((node) =>
    node.addEventListener("click", () => {
      syncRuleFormFromDom();
      ruleFormState.actions.splice(Number(node.dataset.actionDel), 1);
      renderRuleActions();
    }),
  );
}

function syncRuleFormFromDom() {
  const get = (sel) => document.querySelector(sel);
  if (!get("#rule-f-name")) return;
  ruleFormState.name = get("#rule-f-name").value.trim();
  ruleFormState.enabled = !!get("#rule-f-enabled")?.checked;
  ruleFormState.trigger = get("#rule-f-trigger").value;
  // Datasource selection + severity pills are kept in ruleFormState directly by
  // their click handlers (they re-render), so we only read the free-text fields.
  const match = { ...(ruleFormState.match || {}) };
  const rx = get("#rule-f-namerx").value.trim();
  if (rx) match.name_regex = rx; else delete match.name_regex;
  const host = get("#rule-f-host").value.split(",").map((s) => s.trim()).filter(Boolean);
  if (host.length) match.host = host; else delete match.host;
  ruleFormState.match = match;
  const pq = get("#rule-preview-query");
  if (pq) ruleFormState.preview_query = pq.value;
  document.querySelectorAll(".re-action-row").forEach((row, i) => {
    const a = ruleFormState.actions[i];
    if (!a) return;
    row.querySelectorAll("[data-af]").forEach((node) => {
      const f = node.dataset.af;
      if (f === "channels_csv") a.channels = node.value.split(",").map((s) => s.trim()).filter(Boolean);
      else if (f === "seconds" || f === "minutes") a[f] = Number(node.value);
      else a[f] = node.value;
    });
  });
}

async function saveRule() {
  syncRuleFormFromDom();
  const status = document.querySelector("#rule-save-status");
  if (!ruleFormState.name) { if (status) status.textContent = "Name is required."; return; }
  try {
    await postJson("/api/rule", ruleFormState);
    ruleFormState = null;
    pendingRuleEdit = null;
    syncRoute();
    await loadStatus(true);
  } catch (e) {
    if (status) status.textContent = e.message;
  }
}

document.querySelector("#rule-add-button")?.addEventListener("click", () => {
  ruleFormState = blankRule();
  pendingRuleEdit = null;
  syncRoute();
  render(latestReport);
});
document.querySelector("#rule-cancel-button")?.addEventListener("click", () => {
  ruleFormState = null;
  pendingRuleEdit = null;
  syncRoute();
  render(latestReport);
});
document.querySelector("#rule-save-button")?.addEventListener("click", saveRule);

// ── Webhooks / Jira settings ───────────────────────────────────────────────
let jiraFormDirty = false;

function renderWebhooksSettings(report) {
  const jira = (report.integrations && report.integrations.jira) || {};
  const set = (id, val) => { const el = document.querySelector(id); if (el && document.activeElement !== el) el.value = val ?? ""; };
  if (jiraFormDirty) return; // don't clobber in-progress edits
  set("#jira-base-url", jira.base_url);
  set("#jira-email", jira.email);
  set("#jira-project-key", jira.project_key);
  set("#jira-issue-type", jira.issue_type || "Task");
  set("#jira-close-transition", jira.close_transition);
  const enabled = document.querySelector("#jira-enabled");
  if (enabled && document.activeElement !== enabled) enabled.checked = !!jira.enabled;
  const tokenEl = document.querySelector("#jira-api-token");
  if (tokenEl) tokenEl.placeholder = jira.api_token_set ? "•••••• (saved — leave blank to keep)" : "Atlassian API token";
  const statusText = document.querySelector("#jira-status-text");
  const status = document.querySelector("#jira-status");
  if (statusText && status) {
    if (jira.enabled && jira.api_token_set && jira.base_url) { status.className = "ds-status ds-status-on"; statusText.textContent = "Enabled"; }
    else if (jira.api_token_set) { status.className = "ds-status ds-status-off"; statusText.textContent = "Configured (disabled)"; }
    else { status.className = "ds-status ds-status-off"; statusText.textContent = "Not configured"; }
  }
}

function jiraFormPayload() {
  const v = (id) => (document.querySelector(id)?.value || "").trim();
  const payload = {
    enabled: !!document.querySelector("#jira-enabled")?.checked,
    base_url: v("#jira-base-url"),
    email: v("#jira-email"),
    project_key: v("#jira-project-key"),
    issue_type: v("#jira-issue-type") || "Task",
    close_transition: v("#jira-close-transition"),
  };
  const token = v("#jira-api-token");
  if (token) payload.api_token = token;
  return payload;
}

["#jira-base-url", "#jira-email", "#jira-project-key", "#jira-issue-type", "#jira-api-token", "#jira-close-transition"].forEach((id) => {
  document.querySelector(id)?.addEventListener("input", () => { jiraFormDirty = true; });
});

document.querySelector("#jira-test-button")?.addEventListener("click", async (e) => {
  const status = document.querySelector("#jira-save-status");
  e.target.disabled = true;
  if (status) status.textContent = "Testing…";
  try {
    const res = await postJson("/api/integrations/jira/test", jiraFormPayload());
    if (status) status.textContent = "";
    showToast(res.message || "Jira connection OK", "success");
  } catch (err) {
    if (status) status.textContent = "";
    showToast(err.message, "error");
  } finally {
    e.target.disabled = false;
  }
});

document.querySelector("#jira-save-button")?.addEventListener("click", async (e) => {
  const status = document.querySelector("#jira-save-status");
  e.target.disabled = true;
  if (status) status.textContent = "Saving…";
  try {
    await postJson("/api/integrations/jira", jiraFormPayload());
    jiraFormDirty = false;
    if (status) status.textContent = "Saved";
    document.querySelector("#jira-api-token").value = "";
    await loadStatus(true);
    showToast("Jira settings saved", "success");
  } catch (err) {
    if (status) status.textContent = err.message;
    showToast(err.message, "error");
  } finally {
    e.target.disabled = false;
  }
});

// ── Datasources settings ──────────────────────────────────────────────────
let dsFormState = null;
const DS_TYPES = ["prometheus", "alertmanager", "grafana", "zabbix", "elastic"];

function renderDatasourcesSettings(report) {
  const list = document.querySelector("#datasources-list");
  const listPanel = document.querySelector("#ds-list-panel");
  const formPanel = document.querySelector("#ds-form-panel");
  if (!list || !formPanel) return;
  if (dsFormState) {
    listPanel.style.display = "none";
    formPanel.style.display = "";
    renderDatasourceForm();
    return;
  }
  formPanel.style.display = "none";
  listPanel.style.display = "";
  const dss = report.datasources || [];
  if (!dss.length) {
    list.innerHTML = `<div class="empty">No datasources yet. Add Prometheus, Alertmanager, Grafana, Zabbix or Elastic.</div>`;
    return;
  }
  const rules = report.rules || [];
  list.innerHTML = dss
    .map((d) => {
      const type = String(d.type || "prometheus");
      const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
      const host = dsHostFromUrl(d.url) || d.name || typeLabel;
      const mode = d.mode === "webhook" ? "Webhook" : "Polling";
      const usedIn = rules.filter((r) => (r.datasource_ids || []).includes(d.id)).length;
      const status =
        d.enabled === false
          ? `<span class="ds-status ds-status-off"><span class="ds-status-dot"></span>Disabled</span>`
          : `<span class="ds-status ds-status-on"><span class="ds-status-dot"></span>Enabled</span>`;
      const urlRow = d.url
        ? `<div class="ds-card-url">${ICON_LINK} ${escapeHtml(d.url)}</div>`
        : `<div class="ds-card-url ds-card-url-empty">${ICON_LINK} no URL configured</div>`;
      return `<div class="ds-card" data-ds-id="${escapeAttr(d.id)}">
        <div class="ds-card-head">
          <span class="ds-card-icon ds-icon-${escapeAttr(type)}">${dsBrandIcon(type)}</span>
          <div class="ds-card-id">
            <div class="ds-card-title">${escapeHtml(typeLabel)} <span class="ds-card-sep">·</span> ${escapeHtml(host)}</div>
            <div class="ds-card-tags"><span class="ds-badge">${escapeHtml(typeLabel)}</span>${status}</div>
            ${urlRow}
          </div>
        </div>
        <div class="ds-card-cols">
          <div class="ds-col">${ICON_BOLT}<span>${mode}</span></div>
          <div class="ds-col">${ICON_RULES}<span>Used in ${usedIn} rule${usedIn === 1 ? "" : "s"}</span></div>
        </div>
        <div class="ds-card-actions">
          <button class="ds-action" type="button" data-ds-edit="${escapeAttr(d.id)}">${ICON_EDIT} Edit</button>
          <button class="ds-action" type="button" data-ds-test="${escapeAttr(d.id)}">${ICON_PULSE} <span class="ds-action-label">Test connection</span></button>
          <button class="ds-action ds-action-danger" type="button" data-ds-del="${escapeAttr(d.id)}">${ICON_TRASH} Delete</button>
        </div>
      </div>`;
    })
    .join("");
  list.querySelectorAll("[data-ds-edit]").forEach((node) =>
    node.addEventListener("click", () => {
      dsFormState = JSON.parse(JSON.stringify((report.datasources || []).find((d) => d.id === node.dataset.dsEdit) || {}));
      renderDatasourcesSettings(report);
    }),
  );
  list.querySelectorAll("[data-ds-test]").forEach((node) =>
    node.addEventListener("click", async () => {
      const id = node.dataset.dsTest;
      const label = node.querySelector(".ds-action-label");
      const original = label ? label.textContent : "Test connection";
      node.disabled = true;
      if (label) label.textContent = "Testing…";
      try {
        const res = await postJson("/api/datasource/test", { id });
        if (res.ok) {
          showToast(res.message || "Connection OK", "success");
          const card = node.closest(".ds-card");
          const st = card && card.querySelector(".ds-status");
          if (st) { st.className = "ds-status ds-status-on"; st.innerHTML = `<span class="ds-status-dot"></span>Connected`; }
        } else {
          showToast(res.error || "Connection failed", "error");
        }
      } catch (e) {
        showToast(e.message, "error");
      } finally {
        node.disabled = false;
        if (label) label.textContent = original;
      }
    }),
  );
  list.querySelectorAll("[data-ds-del]").forEach((node) =>
    node.addEventListener("click", async () => {
      if (!confirm("Delete this datasource?")) return;
      await postJson("/api/datasource/delete", { id: node.dataset.dsDel });
      await loadStatus(true);
    }),
  );
}

function dsHostFromUrl(url) {
  if (!url) return "";
  try {
    return new URL(url).host || "";
  } catch (e) {
    return String(url).replace(/^[a-z]+:\/\//i, "").split("/")[0];
  }
}

const ICON_LINK = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_BOLT = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M13 3L5 13h6l-1 8 8-10h-6z" stroke-linejoin="round"/></svg>`;
const ICON_RULES = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M4 6h16M4 12h10M4 18h7" stroke-linecap="round"/></svg>`;
const ICON_EDIT = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M4 20h4l10-10-4-4L4 16z" stroke-linejoin="round"/><path d="M13.5 6.5l4 4" stroke-linecap="round"/></svg>`;
const ICON_PULSE = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M3 12h4l2-6 4 12 2-6h6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_TRASH = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M4 7h16M9 7V5h6v2M6 7l1 13h10l1-13" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_DOC = `<svg viewBox="0 0 24 24" fill="none"><path d="M6 3h8l4 4v14H6z" stroke-linejoin="round"/><path d="M14 3v4h4M9 12h6M9 16h6" stroke-linecap="round"/></svg>`;
const ICON_WAND = `<svg viewBox="0 0 24 24" fill="none"><path d="M5 19l9-9M14 6l1.5-1.5M18 10l1.5-1.5M16 4l.7 1.8L18.5 6.5 16.7 7.2 16 9l-.7-1.8L13.5 6.5 15.3 5.8z" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_CHART = `<svg viewBox="0 0 24 24" fill="none"><path d="M4 4v16h16" stroke-linecap="round"/><path d="M7 14l3-3 3 2 4-5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON_JIRA = `<svg class="ds-mini-icon" viewBox="0 0 24 24" fill="none"><path d="M11.5 2.5l9 9a1 1 0 0 1 0 1.4l-7.6 7.6a1 1 0 0 1-1.4 0l-2-2 4.6-4.6a1 1 0 0 0 0-1.4l-4.6-4.6 1.6-1.6a1 1 0 0 1 .4-.2z" stroke-linejoin="round"/></svg>`;
const ICON_WEBHOOK = `<svg viewBox="0 0 24 24" fill="none"><circle cx="7" cy="7" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/><circle cx="6" cy="17" r="2.5"/><path d="M9 8l3.5 6M15 15.5H9.5M8.5 5.5A5 5 0 0 1 17 9" stroke-linecap="round"/></svg>`;

// Brand glyphs (single-path, monochrome — tinted per type via CSS).
function dsBrandIcon(type) {
  if (type === "alertmanager")
    return `<svg viewBox="0 0 24 24" fill="none"><path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2.5h-15z" stroke-linejoin="round"/><path d="M10 19a2 2 0 0 0 4 0" stroke-linecap="round"/></svg>`;
  if (type === "grafana")
    return `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8"/><path d="M8 14a4 4 0 0 1 8 0" stroke-linecap="round"/><circle cx="12" cy="9" r="1.4" fill="currentColor" stroke="none"/></svg>`;
  if (type === "zabbix")
    return `<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="5" width="14" height="14" rx="1"/><path d="M8 8h8l-8 8h8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  if (type === "elastic")
    return `<svg viewBox="0 0 24 24" fill="none"><path d="M5 7h14M7 12h10M10 17h7" stroke-linecap="round"/></svg>`;
  // prometheus (default): flame
  return `<svg viewBox="0 0 24 24" fill="none"><path d="M12 3c1.5 2.5.5 4-1 5.5C9 10 8 12 9 14M12 3c-.5 4 2 5 3 7s.5 5-3 5" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 14a5 5 0 0 0 10 0c0-1.5-.8-2.8-2-3.6.2 1.6-.8 2.6-2 2.6-1.6 0-2-1.4-1.4-2.8C9.6 11 7 12 7 14z" stroke-linejoin="round"/></svg>`;
}

function dsTypeFields(d) {
  const t = d.type || "prometheus";
  const secret = (field, label) =>
    `<label class="form-field"><span>${label}${d[`${field}_set`] ? " (set — leave blank to keep)" : ""}</span><input type="password" data-dsf="${field}" placeholder=""></label>`;
  if (t === "grafana") return secret("token", "API token");
  if (t === "zabbix")
    return `${secret("token", "API token")}
      <label class="form-field"><span>User (if no token)</span><input type="text" data-dsf="user" value="${escapeAttr(d.user || "")}"></label>
      ${secret("password", "Password")}`;
  if (t === "elastic")
    return `<label class="form-field"><span>Index</span><input type="text" data-dsf="index" value="${escapeAttr(d.index || "")}" placeholder=".alerts-*"></label>
      ${secret("api_key", "API key")}
      <label class="form-field"><span>User (if no API key)</span><input type="text" data-dsf="user" value="${escapeAttr(d.user || "")}"></label>
      ${secret("password", "Password")}`;
  return "";
}

function renderDatasourceForm() {
  const d = dsFormState;
  document.querySelector("#ds-form-title").textContent = d.id ? "Edit datasource" : "Add datasource";
  const webhookHint =
    d.mode === "webhook"
      ? `<p class="form-hint">Webhook datasources receive pushes at <code>/api/ingest/${d.type === "alertmanager" || d.type === "grafana" ? d.type : "generic"}</code> using a per-datasource bearer token. ${d.webhook_configured ? "A token is configured." : "Save to generate a token."}</p>`
      : "";
  document.querySelector("#ds-form-body").innerHTML = `
    <div class="form-grid">
      <label class="form-field"><span>Name</span><input id="ds-f-name" type="text" value="${escapeAttr(d.name || "")}" placeholder="e.g. Prod Prometheus"></label>
      <label class="form-field"><span>Type</span><select id="ds-f-type">${DS_TYPES.map((t) => `<option value="${t}" ${d.type === t ? "selected" : ""}>${t}</option>`).join("")}</select></label>
      <label class="form-field"><span>Mode</span><select id="ds-f-mode"><option value="polling" ${d.mode !== "webhook" ? "selected" : ""}>Polling (pull)</option><option value="webhook" ${d.mode === "webhook" ? "selected" : ""}>Webhook (push)</option></select></label>
      <label class="form-field"><span>Enabled</span><select id="ds-f-enabled"><option value="true" ${d.enabled !== false ? "selected" : ""}>Yes</option><option value="false" ${d.enabled === false ? "selected" : ""}>No</option></select></label>
    </div>
    <label class="form-field"><span>URL</span><input id="ds-f-url" type="text" value="${escapeAttr(d.url || "")}" placeholder="http://host:9090"></label>
    <div class="form-grid" id="ds-type-fields">${dsTypeFields(d)}</div>
    ${webhookHint}
    <div id="ds-token-reveal"></div>
    <p class="caption" id="ds-save-status"></p>`;
  document.querySelector("#ds-f-type").addEventListener("change", (e) => {
    syncDsFormFromDom();
    dsFormState.type = e.target.value;
    renderDatasourceForm();
  });
  document.querySelector("#ds-f-mode").addEventListener("change", (e) => {
    syncDsFormFromDom();
    dsFormState.mode = e.target.value;
    renderDatasourceForm();
  });
}

function syncDsFormFromDom() {
  const get = (s) => document.querySelector(s);
  if (!get("#ds-f-name")) return;
  dsFormState.name = get("#ds-f-name").value.trim();
  dsFormState.type = get("#ds-f-type").value;
  dsFormState.mode = get("#ds-f-mode").value;
  dsFormState.enabled = get("#ds-f-enabled").value === "true";
  dsFormState.url = get("#ds-f-url").value.trim();
  document.querySelectorAll("[data-dsf]").forEach((node) => {
    const f = node.dataset.dsf;
    if (node.type === "password" && !node.value) return; // keep existing secret
    dsFormState[f] = node.value;
  });
}

async function saveDatasource() {
  syncDsFormFromDom();
  const status = document.querySelector("#ds-save-status");
  if (!dsFormState.name) { if (status) status.textContent = "Name is required."; return; }
  try {
    const res = await postJson("/api/datasource", dsFormState);
    if (res.ingest_token) {
      // Show the one-time token before leaving the form.
      const reveal = document.querySelector("#ds-token-reveal");
      if (reveal)
        reveal.innerHTML = `<div class="token-reveal"><strong>Ingest token (shown once):</strong><code>${escapeHtml(res.ingest_token)}</code><p class="form-hint">Paste it as the bearer credential in your ${escapeHtml(dsFormState.type)} webhook config (URL <code>${escapeHtml(res.ingest_url || "/api/ingest/generic")}</code>).</p><button class="primary-button" id="ds-token-done" type="button">Done</button></div>`;
      document.querySelector("#ds-token-done")?.addEventListener("click", async () => {
        dsFormState = null;
        await loadStatus(true);
      });
      await fetchStatusInto();
      return;
    }
    dsFormState = null;
    await loadStatus(true);
  } catch (e) {
    if (status) status.textContent = e.message;
  }
}

async function fetchStatusInto() {
  try {
    const r = await fetch("/api/status", { cache: "no-store" });
    latestReport = await r.json();
  } catch (e) {}
}

document.querySelector("#ds-add-button")?.addEventListener("click", () => {
  dsFormState = { name: "", type: "prometheus", mode: "polling", enabled: true, url: "" };
  renderDatasourcesSettings(latestReport || {});
});
document.querySelector("#ds-cancel-button")?.addEventListener("click", () => {
  dsFormState = null;
  renderDatasourcesSettings(latestReport || {});
});
document.querySelector("#ds-save-button")?.addEventListener("click", saveDatasource);

let engineModeInitialized = false;

async function loadStatus(force = false) {
  try {
    if (activePage === "settings" && !mobileAdminOverview) {
      try {
        await loadMobileAdminOverview();
      } catch (error) {
        mobileSecurityStatus.textContent = error.message;
      }
    }
    const response = await fetch("/api/status", { cache: "no-store" });
    const data = await response.json();
    // The Dashboard IS the problems view now, and the sidebar lists problems, so
    // problem data is refreshed every cycle.
    await fetchProblems();
    if (shouldDeferRender(force)) {
      latestReport = data;
      return;
    }
    render(data);
  } catch (error) {
    if (problemsTable) problemsTable.innerHTML = `<tr><td colspan="8" class="empty">Failed to load: ${escapeHtml(error.message)}</td></tr>`;
  }
}

document.querySelectorAll(".nav-button, #activity-button").forEach((node) => {
  node.addEventListener("click", async () => {
    const page = node.dataset.page;
    notificationsOpen = false;
    if (page === "alert") {
      activePage = "alert";
      if (!selectedAlertId && latestReport) {
        const selected = getSelectedAlert(latestReport);
        selectedAlertId = selected?.id || null;
      }
      syncRoute();
      if (latestReport) render(latestReport);
    } else if (page === "rules") {
      activePage = "rules";
      ruleFormState = null;
      pendingRuleEdit = null;
      syncRoute();
      if (latestReport) render(latestReport);
    } else if (page === "settings") {
      activePage = "settings";
      syncRoute();
      try { await loadMobileAdminOverview(); } catch (error) { mobileSecurityStatus.textContent = error.message; }
      if (latestReport) render(latestReport);
    } else {
      activePage = page;
      syncRoute();
      if (latestReport) render(latestReport);
    }
  });
});

const dashboardMoreMetrics = document.querySelector("#dashboard-more-metrics");
if (dashboardMoreMetrics) {
  dashboardMoreMetrics.addEventListener("click", (event) => {
    event.preventDefault();
    activePage = "metrics";
    syncRoute();
    if (latestReport) render(latestReport);
  });
}

document.querySelectorAll(".tab-button[data-tab]").forEach((node) => {
  node.addEventListener("click", () => {
    const nextTab = node.dataset.tab;
    if (!nextTab) return;
    activeTab = nextTab;
    activePage = "alert";
    notificationsOpen = false;
    if (!selectedAlertId && latestReport) {
      const selected = getSelectedAlert(latestReport);
      selectedAlertId = selected?.id || selectedAlertId;
    }
    syncRoute();
    if (latestReport) render(latestReport);
  });
});

document.querySelectorAll("[data-settings-tab]").forEach((node) => {
  node.addEventListener("click", () => {
    activeSettingsTab = node.dataset.settingsTab;
    renderTabs();
  });
});

document.querySelectorAll(".quick-schedule-button").forEach((node) => {
  node.addEventListener("click", () => {
    scheduleInput.value = node.dataset.cron;
    scheduleAlertAutosave();
  });
});

document.querySelector("#agent-custom-enabled").addEventListener("change", (event) => {
  document.querySelector("#custom-agent-fields").style.display = event.target.checked ? "grid" : "none";
});

document.querySelector("#edit-type").addEventListener("change", (event) => {
  updateTypeSpecificFields(event.target.value);
});

document.querySelector("#edit-ssh-eval")?.addEventListener("change", updateSshEvalVisibility);

deleteAlertButton.addEventListener("click", deleteAlert);
document.querySelector("#lock-alert-button")?.addEventListener("click", () => {
  const sel = getSelectedAlert(latestReport);
  setAlertLock(!sel?.config?.locked);
});
rearmAlertButton.addEventListener("click", rearmAlert);
newAlertButton.addEventListener("click", startNewAlert);
newHostButton.addEventListener("click", addHostRow);
document.querySelector("#settings-add-host")?.addEventListener("click", addSettingsHostRow);
homeButton.addEventListener("click", () => {
  activePage = "home";
  selectedHostName = null;
  notificationsOpen = false;
  syncRoute();
  if (latestReport) render(latestReport);
});
if (alertmanagerRefreshButton) {
  alertmanagerRefreshButton.addEventListener("click", () => loadAlertmanagerData());
}
if (alertmanagerSourceForm) {
  alertmanagerSourceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const url = alertmanagerSourceUrl ? alertmanagerSourceUrl.value.trim() : "";
    const name = alertmanagerSourceName ? alertmanagerSourceName.value.trim() : "";
    if (!url) { if (alertmanagerSourceStatus) alertmanagerSourceStatus.textContent = "URL is required"; return; }
    if (alertmanagerSourceStatus) alertmanagerSourceStatus.textContent = "Saving...";
    try {
      const response = await fetch("/api/alertmanager/source", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, name }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed");
      if (alertmanagerSourceStatus) alertmanagerSourceStatus.textContent = "Added";
      if (alertmanagerSourceUrl) alertmanagerSourceUrl.value = "";
      if (alertmanagerSourceName) alertmanagerSourceName.value = "";
      await loadAlertmanagerData();
    } catch (error) {
      if (alertmanagerSourceStatus) alertmanagerSourceStatus.textContent = error.message;
    }
  });
}
globalSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  currentSearchQuery = globalSearchInput.value.trim();
  activePage = "search";
  notificationsOpen = false;
  syncRoute();
  if (latestReport) render(latestReport);
});
copyApiKeyButton.addEventListener("click", async () => {
  const key = apiKeyCreatedValue.textContent.trim();
  if (!key) return;
  await navigator.clipboard.writeText(key);
  copyApiKeyButton.textContent = "Copied!";
  setTimeout(() => { copyApiKeyButton.textContent = "Copy"; }, 2000);
});

apiKeyForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await createApiKey();
  } catch (error) {
    apiKeyCreateStatus.textContent = error.message;
  }
});
mobileEndpointForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await saveMobileEndpointSettings();
  } catch (error) {
    mobileEndpointSaveStatus.textContent = error.message;
  }
});

if (agentsSettingsForm) {
  agentsSettingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (agentsSettingsSaveStatus) agentsSettingsSaveStatus.textContent = "Saving...";
    try {
      const agentUpdates = [...(agentsModelGrid?.querySelectorAll(".agent-model-input") || [])].map((input) => ({
        name: input.dataset.agentName,
        model: input.value.trim() || null,
      }));
      const cooldown = globalAgentCooldown ? parseInt(globalAgentCooldown.value, 10) : 60;
      const response = await fetch("/api/agents/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agents: agentUpdates, agent_cooldown_minutes: isNaN(cooldown) ? 60 : cooldown }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed");
      if (agentsSettingsSaveStatus) agentsSettingsSaveStatus.textContent = "Saved";
    } catch (error) {
      if (agentsSettingsSaveStatus) agentsSettingsSaveStatus.textContent = error.message;
    }
  });
}

if (pipelineSettingsForm) {
  pipelineSettingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pipelineSaveStatus) pipelineSaveStatus.textContent = "Saving...";
    try {
      const payload = {
        ai_pipeline: {
          enabled: pipelineEnabled ? pipelineEnabled.checked : false,
          analysis: { model: pipelineAnalysisModel ? pipelineAnalysisModel.value.trim() || null : null },
          fix:      { model: pipelineFixModel      ? pipelineFixModel.value.trim()      || null : null },
        },
      };
      const response = await fetch("/api/agents/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed");
      if (pipelineSaveStatus) pipelineSaveStatus.textContent = data.ai_pipeline?.enabled ? "Enabled" : "Disabled";
    } catch (error) {
      if (pipelineSaveStatus) pipelineSaveStatus.textContent = error.message;
    }
  });
}

if (fcmForm) {
  fcmForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    fcmSaveStatus.textContent = "Saving...";
    try {
      const response = await fetch("/api/mobile/admin/push-settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          enabled: document.querySelector("#fcm-enabled").checked,
          service_account_path: document.querySelector("#fcm-service-account-path").value.trim(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "failed to save");
      mobileAdminOverview = { ...(mobileAdminOverview || {}), ...data };
      fcmSaveStatus.textContent = data.push?.enabled ? "Enabled" : "Disabled";
    } catch (error) {
      fcmSaveStatus.textContent = error.message;
    }
  });
}

// Pure autosave for settings forms (reuses each form's existing submit handler).
attachFormAutosave(agentsSettingsForm, agentsSettingsSaveStatus);
attachFormAutosave(pipelineSettingsForm, pipelineSaveStatus);
attachFormAutosave(mobileEndpointForm, mobileEndpointSaveStatus);
attachFormAutosave(fcmForm, fcmSaveStatus);

if (testPushButton) {
  testPushButton.addEventListener("click", async () => {
    testPushStatus.textContent = "Sending...";
    testPushButton.disabled = true;
    try {
      const response = await fetch("/api/mobile/admin/test-push", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "failed");
      testPushStatus.textContent = `Sent to ${data.sent}/${data.total} device(s)${data.failed?.length ? ` (failed: ${data.failed.join(", ")})` : ""}`;
    } catch (error) {
      testPushStatus.textContent = error.message;
    } finally {
      testPushButton.disabled = false;
    }
  });
}
if (activityHostFilter) {
  activityHostFilter.addEventListener("change", () => {
    activityHostFilterValue = activityHostFilter.value;
    if (latestReport) render(latestReport);
  });
}
if (activityResultFilter) {
  activityResultFilter.addEventListener("change", () => {
    activityResultFilterValue = activityResultFilter.value;
    if (latestReport) render(latestReport);
  });
}
if (activityExportButton) {
  activityExportButton.addEventListener("click", () => {
    if (latestReport) exportActivityCsv(latestReport);
  });
}
if (maintenanceForm) {
  maintenanceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    maintenanceSaveStatus.textContent = "Saving...";
    try {
      const scope = maintenanceScope.value;
      const selectedAlert = (latestReport?.alert_rules || []).find((item) => String(item.id || item.name) === maintenanceAlert.value);
      const response = await fetch("/api/maintenance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scope,
          host: maintenanceHost.value,
          alert_id: scope === "alert" ? (selectedAlert?.id || "") : "",
          alert_name: scope === "alert" ? (selectedAlert?.name || "") : "",
          starts_at: new Date(maintenanceStartsAt.value).toISOString(),
          ends_at: new Date(maintenanceEndsAt.value).toISOString(),
          reason: maintenanceReason.value.trim(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "failed to save");
      maintenanceSaveStatus.textContent = data.window?.active ? "Active now" : "Scheduled";
      maintenanceForm.reset();
      await loadStatus(true);
    } catch (error) {
      maintenanceSaveStatus.textContent = error.message;
    }
  });
}
notificationsButton.addEventListener("click", () => {
  notificationsOpen = !notificationsOpen;
  if (latestReport) renderNotifications(latestReport);
});

alertSearch.addEventListener("input", () => latestReport && renderAlertList(latestReport));

window.addEventListener("popstate", () => {
  readRoute();
  // Reconcile the rule editor with the URL: /rules/<id>/edit (pendingRuleEdit)
  // reopens it; plain /rules closes it.
  if (activePage === "rules" && !pendingRuleEdit) ruleFormState = null;
  if (latestReport) render(latestReport);
});

document.addEventListener("click", (event) => {
  if (!notificationsOpen) return;
  if (notificationsPopup.contains(event.target) || notificationsButton.contains(event.target)) return;
  notificationsOpen = false;
  if (latestReport) renderNotifications(latestReport);
});

readRoute();
loadStatus();
setInterval(loadStatus, 60000);
