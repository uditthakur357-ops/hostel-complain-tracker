const $ = (id) => document.getElementById(id);

let allComplaints = [];

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (const item of cookies) {
    const cookie = item.trim();
    if (cookie.startsWith(name + "=")) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return "";
}

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;",
    '"': "&quot;", "'": "&#39;"
  })[char]);
}

function showMessage(message, type = "error") {
  const box = $("formMessage");
  box.textContent = message;
  box.className = "form-message " + type;
}

async function loadComplaints() {
  $("complaintsList").innerHTML =
    '<div class="loading-state"><span class="spinner"></span><p>Loading complaints...</p></div>';

  try {
    const response = await fetch("/api/complaints/", {
      headers: { "Accept": "application/json" },
      credentials: "same-origin"
    });

    if (response.status === 401 || response.redirected) {
      window.location.href = "/login/";
      return;
    }

    if (!response.ok) throw new Error("Could not load complaints.");

    const data = await response.json();
    allComplaints = data.complaints || [];

    $("userName").textContent =
      data.full_name || data.username || "Student";
    $("avatar").textContent =
      (data.full_name || data.username || "S").charAt(0).toUpperCase();

    $("totalCount").textContent = data.total_count ?? allComplaints.length;
    $("pendingCount").textContent = data.pending_count ?? 0;
    $("resolvedCount").textContent = data.resolved_count ?? 0;
    $("overdueCount").textContent = data.overdue_count ?? 0;

    $("chartTotal").textContent = data.total_count ?? allComplaints.length;
    $("legendResolved").textContent = data.resolved_count ?? 0;
    $("legendPending").textContent = data.pending_count ?? 0;
    $("legendOverdue").textContent = data.overdue_count ?? 0;

    updateChart();
    renderComplaints();
  } catch (error) {
    $("complaintsList").innerHTML =
      '<div class="empty-state"><b>Could not load reports</b><p>Check that the Django server is running, then refresh.</p></div>';
    $("listCount").textContent = "Connection issue";
  }
}

function updateChart() {
  const total = allComplaints.length;
  const resolved = allComplaints.filter(c => c.status === "Resolved").length;
  const overdue = allComplaints.filter(c => c.is_overdue).length;
  const pending = Math.max(0, total - resolved - overdue);

  const resolvedDeg = total ? resolved / total * 360 : 0;
  const pendingDeg = total ? pending / total * 360 : 0;
  const overdueDeg = total ? overdue / total * 360 : 0;

  $("donutChart").style.background = total
    ? `conic-gradient(#08d6a0 0deg ${resolvedDeg}deg, #ffb629 ${resolvedDeg}deg ${resolvedDeg + pendingDeg}deg, #ff4568 ${resolvedDeg + pendingDeg}deg ${resolvedDeg + pendingDeg + overdueDeg}deg, #16324e ${resolvedDeg + pendingDeg + overdueDeg}deg 360deg)`
    : "#16324e";
}

function renderComplaints() {
  const search = (
    ($("searchInput").value || "") + " " +
    ($("listSearch").value || "")
  ).trim().toLowerCase();

  const status = $("statusFilter").value;
  const type = $("typeFilter").value;

  const filtered = allComplaints.filter(c => {
    const text = [
      c.title, c.description, c.ticket_number,
      c.complaint_type, c.hostel_block, c.room_number, c.status
    ].join(" ").toLowerCase();

    return (!search || text.includes(search)) &&
      (!status || c.status === status) &&
      (!type || c.complaint_type === type);
  });

  $("listCount").textContent =
    `Showing ${filtered.length} of ${allComplaints.length} reports`;

  if (!filtered.length) {
    $("complaintsList").innerHTML = `
      <div class="empty-state">
        <i data-lucide="clipboard-list"></i>
        <b>${allComplaints.length ? "No matching complaints" : "No complaints yet"}</b>
        <p>${allComplaints.length
          ? "Try changing your search or filters."
          : "Submit your first complaint using the form."}</p>
      </div>`;
    if (window.lucide) lucide.createIcons();
    return;
  }

  $("complaintsList").innerHTML = filtered.map(c => {
    const category = String(c.complaint_type || "Other").toLowerCase();
    const icon = {
      water: "droplets",
      electricity: "zap",
      internet: "wifi",
      cleaning: "brush",
      other: "message-circle"
    }[category] || "message-circle";

    const statusClass = c.status === "Resolved"
      ? "resolved"
      : c.status === "In Progress" ? "in-progress" : "open";

    const priority = String(c.priority || "Medium").toLowerCase();
    const priorityClass = ["low", "medium", "high"].includes(priority)
      ? priority : "medium";

    const overdue = c.is_overdue && c.status !== "Resolved";

    return `
      <div class="complaint-item">
        <div class="complaint-icon ${escapeHTML(category)}">
          <i data-lucide="${icon}"></i>
        </div>
        <div class="complaint-info">
          <h3>${escapeHTML(c.title)}</h3>
          <div class="complaint-meta">
            <span class="ticket">#${escapeHTML(c.ticket_number)}</span>
            · ${escapeHTML(c.created_at)}
          </div>
        </div>
        <div class="complaint-tags">
          <span class="priority-badge ${priorityClass}">
            ${escapeHTML(c.priority || "Medium")}
          </span>
          <span class="status-badge ${overdue ? "open" : statusClass}">
            ${overdue ? "Overdue" : escapeHTML(c.status)}
          </span>
        </div>
        <div class="complaint-detail">
          <b>${escapeHTML(c.complaint_type)}</b>
          · Block ${escapeHTML(c.hostel_block)}
          · Room ${escapeHTML(c.room_number)}
          <p>${escapeHTML(c.description)}</p>
          ${c.staff_note
            ? `<p><b>Staff update:</b> ${escapeHTML(c.staff_note)}</p>`
            : ""}
        </div>
      </div>`;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

$("complaintDescription").addEventListener("input", () => {
  $("charCount").textContent = $("complaintDescription").value.length;
});

$("complaintForm").addEventListener("submit", async event => {
  event.preventDefault();

  const button = $("submitBtn");
  button.disabled = true;
  button.innerHTML = '<span class="spinner"></span> Submitting...';
  showMessage("");

  const payload = {
    complaint_type: $("complaintType").value,
    title: $("complaintTitle").value.trim(),
    description: $("complaintDescription").value.trim(),
    hostel_block: $("hostelBlock").value.trim(),
    room_number: $("roomNumber").value.trim()
  };

  try {
    const response = await fetch("/api/complaints/create/", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.status === 401 || response.redirected) {
      window.location.href = "/login/";
      return;
    }

    if (!response.ok) {
      const errors = data.errors
        ? Object.entries(data.errors)
            .map(([field, messages]) => `${field}: ${messages.join(", ")}`)
            .join(" | ")
        : data.error || "Please check the form and try again.";
      throw new Error(errors);
    }

    showMessage(
      `Complaint submitted successfully! Ticket: ${data.ticket_number}`,
      "success"
    );

    $("complaintForm").reset();
    $("charCount").textContent = "0";

    await loadComplaints();
  } catch (error) {
    showMessage(error.message || "Something went wrong. Please try again.");
  } finally {
    button.disabled = false;
    button.innerHTML =
      '<i data-lucide="send"></i> Submit complaint <i data-lucide="arrow-right"></i>';
    if (window.lucide) lucide.createIcons();
  }
});

$("searchInput").addEventListener("input", renderComplaints);
$("listSearch").addEventListener("input", renderComplaints);
$("statusFilter").addEventListener("change", renderComplaints);
$("typeFilter").addEventListener("change", renderComplaints);
$("refreshBtn").addEventListener("click", loadComplaints);

$("clearFilters").addEventListener("click", () => {
  $("searchInput").value = "";
  $("listSearch").value = "";
  $("statusFilter").value = "";
  $("typeFilter").value = "";
  renderComplaints();
});

$("logoutBtn").addEventListener("click", async () => {
  if (!confirm("Are you sure you want to sign out?")) return;

  try {
    const response = await fetch("/api/logout/", {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

    if (response.ok) {
      window.location.href = "/login/";
    } else {
      alert("Logout failed. Please try again.");
    }
  } catch {
    alert("Could not connect to the server.");
  }
});

document.querySelectorAll(".nav-link").forEach(link => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".nav-link")
      .forEach(item => item.classList.remove("active"));
    link.classList.add("active");
  });
});

if (window.lucide) lucide.createIcons();
loadComplaints();