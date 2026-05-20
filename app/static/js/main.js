let charts = {};

// ==========================================
// 1. Dynamic Profile Dropdowns Logic
// ==========================================
function setupDynamicDropdowns() {
    for (let i = 1; i <= 3; i++) {
        const trackSelect = document.getElementById(`track_${i}`);
        const profileSelect = document.getElementById(`profile_${i}`);
        
        if (!trackSelect || !profileSelect) continue;

        // لو في تراك محتار من الأول (في حالة التعديل Edit) يفتح الـ Profile
        if (trackSelect.value) {
            profileSelect.removeAttribute('disabled');
        }

        trackSelect.addEventListener('change', function() {
            const trackId = this.value;
            profileSelect.innerHTML = '<option value="">Select Profile...</option>';
            
            if (trackId) {
                // فتح الـ dropdown ونجيب الداتا
                profileSelect.removeAttribute('disabled');
                fetch(`/api/lookups/profiles/${trackId}`)
                    .then(res => res.json())
                    .then(data => {
                        data.forEach(p => {
                            const opt = document.createElement('option');
                            opt.value = p.id;
                            opt.textContent = p.name;
                            profileSelect.appendChild(opt);
                        });
                    })
                    .catch(err => console.error("Error fetching profiles:", err));
            } else {
                // قفل الـ dropdown لو المستخدم مسح اختيار التراك
                profileSelect.setAttribute('disabled', 'disabled');
            }
        });
    }
}

// ==========================================
// 2. Chart Theme Helper
// ==========================================
function getChartThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        text: isDark ? '#94a3b8' : '#7f8c8d',
        grid: isDark ? '#334155' : '#e0e6ed',
        tooltipBg: isDark ? '#1e293b' : '#ffffff',
        tooltipText: isDark ? '#f1f5f9' : '#2c3e50'
    };
}

// ==========================================
// 3. Dashboard Initialization & API Calls
// ==========================================
function initDashboard() {
    const c = getChartThemeColors();
    
    // Default Options for standard charts
    const chartOpts = {
        responsive: true, 
        maintainAspectRatio: false,
        plugins: { 
            legend: { labels: { color: c.text, font: { family: 'Inter' } } },
            tooltip: { backgroundColor: c.tooltipBg, titleColor: c.tooltipText, bodyColor: c.tooltipText }
        },
        scales: { 
            x: { ticks: { color: c.text, font: { family: 'Inter' } }, grid: { color: c.grid } }, 
            y: { ticks: { color: c.text, font: { family: 'Inter' } }, grid: { color: c.grid }, beginAtZero: true } 
        }
    };

    // Default Options for Pie/Doughnut charts
    const pieOpts = { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { 
            legend: { position: 'bottom', labels: { color: c.text, padding: 15, font: { family: 'Inter' } } },
            tooltip: { backgroundColor: c.tooltipBg, titleColor: c.tooltipText, bodyColor: c.tooltipText }
        } 
    };

    // --- 1. Fetch KPIs ---
    fetch('/dashboard/api/kpis').then(r=>r.json()).then(d => {
        document.getElementById('kpi-total').innerText = d.total;
        document.getElementById('kpi-approved').innerText = d.approved;
        document.getElementById('kpi-rejected').innerText = d.rejected;
        document.getElementById('kpi-pending').innerText = d.pending;
        document.getElementById('kpi-rate').innerText = d.avg_rate + ' EGP';
        document.getElementById('kpi-b2b-b2c').innerText = `${d.b2b} / ${d.b2c}`;
    });

    // --- 2. Performance by Track (Stacked Bar) ---
    fetch('/dashboard/api/track-performance').then(r=>r.json()).then(data => {
        charts.trackPerf = new Chart(document.getElementById('chartTrackPerf'), {
            type: 'bar',
            data: { 
                labels: data.map(d=>d.name), 
                datasets: [
                    { label: 'Approved', data: data.map(d=>d.approved), backgroundColor: '#4cc9f0' },
                    { label: 'Pending', data: data.map(d=>d.pending), backgroundColor: '#f8961e' },
                    { label: 'Rejected', data: data.map(d=>d.rejected), backgroundColor: '#f72585' }
                ]
            },
            options: { 
                ...chartOpts, 
                scales: { x:{...chartOpts.scales.x, stacked:true}, y:{...chartOpts.scales.y, stacked:true} } 
            }
        });
    });

    // --- 3. Approval Distribution (Doughnut) ---
    fetch('/dashboard/api/approval-distribution').then(r=>r.json()).then(data => {
        charts.approvalDist = new Chart(document.getElementById('chartApprovalDist'), {
            type: 'doughnut',
            data: { 
                labels: Object.keys(data), 
                datasets: [{ data: Object.values(data), backgroundColor: ['#4cc9f0', '#f72585', '#f8961e'], borderWidth: 0 }] 
            },
            options: pieOpts
        });
    });

    // --- 4. Track Distribution (Pie) ---
    fetch('/dashboard/api/track-distribution').then(r=>r.json()).then(data => {
        charts.trackDist = new Chart(document.getElementById('chartTrackDist'), {
            type: 'pie',
            data: { 
                labels: data.map(d=>d.name), 
                datasets: [{ data: data.map(d=>d.count), backgroundColor: ['#4361ee', '#4cc9f0', '#f72585', '#f8961e', '#7209b7'], borderWidth: 0 }] 
            },
            options: pieOpts
        });
    });

    // --- 5. B2B vs B2C by Track (Grouped Bar) ---
    fetch('/dashboard/api/b2b-b2c-track').then(r=>r.json()).then(data => {
        charts.b2bB2c = new Chart(document.getElementById('chartB2bB2c'), {
            type: 'bar',
            data: { 
                labels: data.map(d=>d.name), 
                datasets: [
                    { label: 'B2B', data: data.map(d=>d.b2b), backgroundColor: '#4361ee' },
                    { label: 'B2C', data: data.map(d=>d.b2c), backgroundColor: '#f8961e' }
                ]
            },
            options: chartOpts
        });
    });

    // --- 6. Profile Distribution (Horizontal Bar) ---
    fetch('/dashboard/api/profile-distribution').then(r=>r.json()).then(data => {
        charts.profileDist = new Chart(document.getElementById('chartProfileDist'), {
            type: 'bar',
            data: { 
                labels: data.map(d=>d.name), 
                datasets: [{ label: 'Instructors', data: data.map(d=>d.count), backgroundColor: '#7209b7' }] 
            },
            options: { ...chartOpts, indexAxis: 'y' }
        });
    });
        // --- New vs Current by Track (Chart + Table) ---
    fetch('/dashboard/api/track-status').then(r=>r.json()).then(data => {
        // 1. رسم الـ Chart
        charts.trackStatus = new Chart(document.getElementById('chartTrackStatus'), {
            type: 'bar',
            data: { 
                labels: data.map(d=>d.name), 
                datasets: [
                    { label: 'New Instructors', data: data.map(d=>d.new), backgroundColor: '#4361ee' },
                    { label: 'Current Instructors', data: data.map(d=>d.current), backgroundColor: '#4cc9f0' }
                ]
            },
            options: chartOpts
        });

        // 2. تعبئة الجدول بجانبه بالأرقام والاسماء
        const tbody = document.getElementById('track-status-table-body');
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No data yet.</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(d => `
            <tr>
                <td class="fw-bold">${d.name}</td>
                <td class="text-center">
                    <span class="badge" style="background-color: #4361ee; color: white;">${d.new}</span>
                </td>
                <td class="text-center">
                    <span class="badge" style="background-color: #4cc9f0; color: #000;">${d.current}</span>
                </td>
            </tr>
        `).join('');
    });

        // --- Daily Approval Trend (Line) ---
    fetch('/dashboard/api/daily-trend').then(r=>r.json()).then(data => {
        charts.dailyTrend = new Chart(document.getElementById('chartDailyTrend'), {
            type: 'line',
            data: { 
                labels: data.map(d=>d.day), 
                datasets: [
                    { label: 'Approved', data: data.map(d=>d.approved), borderColor: '#4cc9f0', backgroundColor: 'rgba(76, 201, 240, 0.1)', tension: 0.4, fill: true },
                    { label: 'Rejected', data: data.map(d=>d.rejected), borderColor: '#f72585', backgroundColor: 'rgba(247, 37, 133, 0.1)', tension: 0.4, fill: true },
                    { label: 'Pending', data: data.map(d=>d.pending), borderColor: '#f8961e', backgroundColor: 'rgba(248, 150, 30, 0.1)', tension: 0.4, fill: true }
                ]
            },
            options: chartOpts
        });
    });
    
    // ==========================================
    // 4. Tables Population Helper & Fetches
    // ==========================================
    const populateTable = (id, data, mapper) => { 
        document.getElementById(id).innerHTML = data.map(mapper).join(''); 
    };

    // Leaderboard Table
    fetch('/dashboard/api/leaderboard').then(r=>r.json()).then(data => {
        populateTable('leaderboard-body', data, (d,i) => 
            `<tr><td class="fw-bold">${i+1}</td><td>${d.name}</td><td><span class="score-badge">${d.score}</span></td><td class="text-end">${d.rate} EGP</td></tr>`
        );
    });

    // Aging Analysis Table
    fetch('/dashboard/api/aging-analysis').then(r=>r.json()).then(data => {
        populateTable('aging-body', Object.entries(data), ([k,v]) => 
            `<tr><td>${k}</td><td class="text-end fw-bold">${v}</td></tr>`
        );
    });

    // Cost Analysis Table
    fetch('/dashboard/api/cost-analysis').then(r=>r.json()).then(data => {
        populateTable('cost-body', data, d => 
            `<tr><td>${d.name}</td><td class="text-end fw-bold">${d.avg_rate} EGP</td></tr>`
        );
    });

    // Business Type Performance Table
    fetch('/dashboard/api/business-performance').then(r=>r.json()).then(data => {
        populateTable('biz-body', data, d => 
            `<tr><td class="fw-bold">${d.type}</td><td class="text-center">${d.total}</td><td class="text-center">${d.approved}</td><td class="text-end fw-bold text-primary">${d.success_rate}%</td></tr>`
        );
    });
    
    // Plans Progress Table
    fetch('/dashboard/api/plans-progress').then(r=>r.json()).then(data => {
        const tbody = document.getElementById('plans-progress-body');
        if(data.length === 0) { tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No active hiring plans.</td></tr>'; return; }
        tbody.innerHTML = data.map(p => {
            let barColor = 'bg-danger';
            if(p.percentage >= 100) barColor = 'bg-success';
            else if(p.percentage >= 50) barColor = 'bg-warning';
            return `<tr>
                <td class="fw-bold">${p.title}</td>
                <td class="text-muted small">${p.start_date}</td>
                <td class="text-center"><span class="badge bg-primary bg-opacity-10 text-primary">${p.target}</span></td>
                <td class="text-center fw-bold">${p.actual}</td>
                <td class="text-center fw-bold text-success">${p.approved}</td>
                <td class="text-center text-warning fw-bold">${p.pending}</td>
                <td class="text-center text-danger fw-bold">${p.rejected}</td>
                <td class="text-center text-danger fw-bold">${p.gap > 0 ? p.gap : '<i class="bi bi-check-circle-fill text-success"></i>'}</td>
                <td style="min-width: 150px;"><div class="progress" style="height: 8px;"><div class="progress-bar ${barColor}" style="width: ${p.percentage}%"></div></div><small class="text-muted">${p.percentage}%</small></td>
                <td>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${p.approved_progress >= 100 ? 'bg-success' : (p.approved_progress >= 50 ? 'bg-warning' : 'bg-danger')}" style="width: ${p.approved_progress}%"></div>
                    </div>
                    <small class="text-muted">${p.approved_progress}%</small>
                </td>
            </tr>`;
        }).join('');
    }).catch(err => console.error(err));

        // Plans Detailed Granular Breakdown
    fetch('/dashboard/api/plans-detailed-breakdown').then(r=>r.json()).then(data => {
        const tbody = document.getElementById('plans-breakdown-body');
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No plan requirements found.</td></tr>';
            return;
        }
        
        let currentPlan = "";
        let html = "";
        
        data.forEach(p => {
            // لو اسم الخطة تغير، نطبع سطر عنوان للخطة عشان نفصل بينهم (لو في أكتر من خطة)
            if (p.plan_title !== currentPlan) {
                currentPlan = p.plan_title;
                html += `
                    <tr style="background-color: var(--input-bg);">
                        <td colspan="9" class="fw-bold text-primary pt-3 pb-3" style="font-size: 0.95rem;">
                            <i class="bi bi-folder2-open me-2"></i>${p.plan_title}
                        </td>
                    </tr>`;
            }
            
            // سطر البيانات
            html += `
                <tr>
                    <td></td>
                    <td class="fw-bold">${p.track_name}</td>
                    <td class="text-muted small">${p.profile_name}</td>
                    <td class="text-center"><span class="badge bg-secondary bg-opacity-10 text-secondary">${p.target}</span></td>
                    <td class="text-center"><span class="badge bg-primary bg-opacity-10 text-primary">${p.actual}</span></td>
                    <td class="text-center">
                        <span class="badge bg-${p.status_color} bg-opacity-10 text-${p.status_color} p-2">
                            ${p.status} (${p.actual}/${p.target})
                        </span>
                    </td>
                    <td class="text-center fw-bold">${p.approved}</td>
                    <td class="text-center fw-bold">${p.pending}</td>
                    <td class="text-center fw-bold">${p.rejected}</td>
                </tr>`;
        });
        
        tbody.innerHTML = html;
    }).catch(err => console.error(err));
}

// ==========================================
// 5. Update Charts Theme Dynamically
// ==========================================
function updateChartsTheme(theme) {
    const c = getChartThemeColors();
    
    Object.values(charts).forEach(chart => {
        // Update Axes (for Bar/Line charts)
        if(chart.options.scales) {
            Object.values(chart.options.scales).forEach(scale => {
                if(scale.ticks) scale.ticks.color = c.text;
                if(scale.grid) scale.grid.color = c.grid;
            });
        }
        // Update Legends (for all charts)
        if(chart.options.plugins?.legend) {
            chart.options.plugins.legend.labels.color = c.text;
        }
        // Update Tooltips (for all charts)
        if(chart.options.plugins?.tooltip) {
            chart.options.plugins.tooltip.backgroundColor = c.tooltipBg;
            chart.options.plugins.tooltip.titleColor = c.tooltipText;
            chart.options.plugins.tooltip.bodyColor = c.tooltipText;
        }
        
        chart.update('none'); // 'none' prevents animation on theme change for smoother feel
    });
}

// ==========================================
// 6. Run on Page Load
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Dashboard Charts if we are on the dashboard page
    if (document.getElementById('chartTrackPerf')) {
        initDashboard();
    }
    
    // Initialize Dynamic Dropdowns if we are on create/edit forms
    setupDynamicDropdowns();
});