import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Asset Sync – Warehouse Device Monitoring",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# CUSTOM STYLING (MATCHING THE ORIGINAL DASHBOARD)
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Background subtle gradient */
    .stApp {
        background: radial-gradient(900px 420px at 88% -8%, #e0e7ff 0, transparent 60%),
                    radial-gradient(700px 400px at -5% 8%, #cffafe 0, transparent 55%),
                    #f7f8fc;
    }

    /* Cards */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e6e9f2;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 16px 34px -22px rgba(60,70,150,.25);
        margin-bottom: 16px;
    }

    .kpi-container {
        background: #ffffff;
        border: 1px solid #e6e9f2;
        border-radius: 18px;
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 1px 2px rgba(16,24,40,.04);
        margin-bottom: 10px;
    }
    
    .kpi-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    
    .kpi-title {
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 2px;
    }
    
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: #0f172a;
    }
    
    .kpi-sub {
        font-size: 12px;
        color: #64748b;
        margin-top: 2px;
    }

    /* Status Pills */
    .pill {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 12px;
        font-weight: 700;
    }
    .pill-ok { background: #dcfaee; color: #047857; }
    .pill-wa { background: #fef3d6; color: #a16207; }
    .pill-cr { background: #fee2e2; color: #b91c1c; }
    .pill-in { background: #e0e7ff; color: #3730a3; }

    /* Live indicator */
    .live-badge {
        color: #10b981;
        font-size: 12px;
        font-weight: 600;
        background: #e8faf3;
        padding: 6px 14px;
        border-radius: 99px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
    }

    /* Sidebar info */
    .sync-box {
        border-radius: 16px;
        padding: 14px;
        background: linear-gradient(160deg,#eef2ff,#ecfeff);
        border: 1px solid #e6e9f2;
        font-size: 12px;
        color: #64748b;
        margin-top: 20px;
    }
    .sync-box b {
        color: #0f172a;
        display: block;
        font-size: 13px;
        margin-bottom: 4px;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 11px;
        font-weight: 600;
        border: 1px solid #e6e9f2;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        border-color: #4f46e5;
        color: #4f46e5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# CONSTANTS & INITIAL DATA
# ==========================================
SITES = ["Chakan FC", "Bhosari MIDC", "Hadapsar Hub"]
TYPES = {
    "laptop": ("Laptop", "💻"),
    "desktop": ("Desktop PC", "🖥️"),
    "monitor": ("Monitor", "🖵"),
    "printer": ("Printer", "🖨️"),
    "scanner": ("Barcode scanner", "🔎"),
    "router": ("Router / Wi‑Fi", "📶"),
    "cctv": ("CCTV camera", "📹"),
    "phone": ("Phone / tablet", "📱"),
    "ups": ("UPS", "🔋"),
}

DEFAULT_BASE = [
    ("Dispatch Desk", "desktop", "Dell OptiPlex", "Windows 11"),
    ("Inbound Laptop", "laptop", "Lenovo ThinkPad", "Windows 11"),
    ("Packing Monitor", "monitor", "Dell P2422H", "Display"),
    ("Label Printer", "printer", "Zebra ZD421", "FW 5.2"),
    ("Handheld Scanner", "scanner", "Honeywell CT40", "Android 11"),
    ("Wi‑Fi Router", "router", "TP‑Link Omada", "FW 5.1"),
    ("Dock Camera", "cctv", "Hikvision", "FW 5.7"),
    ("Floor Tablet", "phone", "Samsung Tab A8", "Android 13"),
    ("Rack UPS", "ups", "APC Smart‑UPS", "FW 2.1"),
]

OFF_KEYS = {"1-4", "2-5"}
WARN_KEYS = {"0-3", "1-7", "2-6"}

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "devices" not in st.session_state:
    devs = []
    dev_id = 0
    for s_idx in range(3):
        for b_idx, b in enumerate(DEFAULT_BASE):
            k = f"{s_idx}-{b_idx}"
            st_val = "off" if k in OFF_KEYS else ("warn" if k in WARN_KEYS else "on")
            devs.append({
                "id": dev_id,
                "name": f"{b[0]} {s_idx + 1}",
                "type": b[1],
                "brand": b[2],
                "os": b[3],
                "ip": f"192.168.{10 + s_idx * 10}.{20 + b_idx * 9}",
                "site_idx": s_idx,
                "site": SITES[s_idx],
                "status": st_val,
                "cpu": random.randint(20, 75),
                "memory": random.randint(30, 85),
                "storage": random.randint(25, 70),
                "signal": random.randint(70, 99),
                "uptime_days": random.randint(3, 28)
            })
            dev_id += 1
    st.session_state.devices = devs

if "alerts" not in st.session_state:
    st.session_state.alerts = [
        {"id": 1, "level": "cr", "text": "Handheld Scanner 2 offline – last seen 4 min ago", "site": "Bhosari MIDC", "time": "4 min ago", "ack": False},
        {"id": 2, "level": "cr", "text": "Wi‑Fi Router 3 offline – packing zone has no network", "site": "Hadapsar Hub", "time": "9 min ago", "ack": False},
        {"id": 3, "level": "wa", "text": "Label Printer 1 running low on media", "site": "Chakan FC", "time": "15 min ago", "ack": False},
        {"id": 4, "level": "wa", "text": "Floor Tablet 2 battery below 10%", "site": "Bhosari MIDC", "time": "22 min ago", "ack": False},
        {"id": 5, "level": "wa", "text": "Dock Camera 3 recording gap detected", "site": "Hadapsar Hub", "time": "40 min ago", "ack": False},
        {"id": 6, "level": "in", "text": "Firmware 5.8 available for 3 CCTV cameras", "site": "Chakan FC", "time": "1 h ago", "ack": False},
    ]

if "discovered" not in st.session_state:
    st.session_state.discovered = [
        {"name": "Reception Laptop", "type": "laptop", "ip": "192.168.10.77", "site_idx": 0, "brand": "HP ProBook"},
        {"name": "HP LaserJet Office", "type": "printer", "ip": "192.168.20.64", "site_idx": 1, "brand": "HP LaserJet"},
        {"name": "Gate Camera", "type": "cctv", "ip": "192.168.30.91", "site_idx": 2, "brand": "Hikvision"},
        {"name": "Samsung Monitor", "type": "monitor", "ip": "192.168.30.58", "site_idx": 2, "brand": "Samsung UHD"},
    ]

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
            <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #4f46e5, #06b6d4); display: grid; place-items: center; color: white; font-size: 22px; font-weight: 800; box-shadow: 0 10px 24px -8px #4f46e5;">
                ⟳
            </div>
            <div>
                <span style="font-size: 20px; font-weight: 800; letter-spacing: -0.03em; color: #0f172a;">Asset Sync</span>
                <span style="display: block; font-size: 11.5px; color: #64748b;">Pune warehouse network</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["Dashboard", "Devices", "Connect Device", "Alerts", "Warehouses", "Reports"],
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="sync-box">
            <b>3 warehouses synced</b>
            Chakan · Bhosari · Hadapsar<br>
            Status: <span style="color:#10b981; font-weight:600;">Active Live Stream</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# PAGE ROUTING
# ==========================================

# HEADER ROW
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    titles = {
        "Dashboard": ("Dashboard", "Live overview of every connected device across Pune"),
        "Devices": ("Devices", "Every laptop, monitor, printer, scanner and camera in one list"),
        "Connect Device": ("Connect a Device", "Add everyday warehouse devices in three simple steps"),
        "Alerts": ("Alerts", "Problems detected across your devices, newest first"),
        "Warehouses": ("Warehouses", "Three Pune locations, one view"),
        "Reports": ("Reports", "Trends and reliability insights across the fleet"),
    }
    t, s = titles[page]
    st.markdown(f"<h1 style='margin:0; font-size:28px; letter-spacing:-0.03em;'>{t}</h1><p style='color:#64748b; font-size:14px; margin-top:2px;'>{s}</p>", unsafe_allow_html=True)

with header_col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
            <span class="live-badge"><span class="live-dot"></span> Live monitoring</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if page == "Dashboard":
    devices = st.session_state.devices
    total = len(devices)
    online = len([d for d in devices if d["status"] == "on"])
    offline = len([d for d in devices if d["status"] == "off"])
    open_alerts = [a for a in st.session_state.alerts if not a["ack"]]
    critical_alerts = len([a for a in open_alerts if a["level"] == "cr"])

    # 4 Top KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-icon" style="background:#e0e7ff;">🔌</div>
            <div>
                <div class="kpi-title">Connected devices</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-sub">3 warehouses</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        pct_healthy = round((online / total) * 100, 1) if total else 0
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-icon" style="background:#dcfaee;">✅</div>
            <div>
                <div class="kpi-title">Online now</div>
                <div class="kpi-value">{online}</div>
                <div class="kpi-sub">{pct_healthy}% healthy</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-icon" style="background:#fee2e2;">⛔</div>
            <div>
                <div class="kpi-title">Offline</div>
                <div class="kpi-value">{offline}</div>
                <div class="kpi-sub">needs attention</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-icon" style="background:#fef3d6;">🔔</div>
            <div>
                <div class="kpi-title">Open alerts</div>
                <div class="kpi-value">{len(open_alerts)}</div>
                <div class="kpi-sub">{critical_alerts} critical</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # CHARTS ROW 1
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Fleet Uptime Trend</h3><span style='color:#64748b; font-size:13px;'>Last 30 readings · Average <b>98.4%</b></span>", unsafe_allow_html=True)
        # Generate smooth area chart
        chart_data = [96.5 + (i * 0.08) + random.uniform(-0.5, 0.6) for i in range(30)]
        fig_uptime = go.Figure()
        fig_uptime.add_trace(go.Scatter(
            y=chart_data,
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(79, 70, 229, 0.12)',
            line=dict(color='#4f46e5', width=3, shape='spline'),
            name="Uptime %"
        ))
        fig_uptime.update_layout(
            height=210,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(range=[94, 100], gridcolor='#e6e9f2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_uptime, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Device Types</h3><span style='color:#64748b; font-size:13px;'>Inventory distribution</span>", unsafe_allow_html=True)
        type_counts = {}
        for d in devices:
            t_name = TYPES[d["type"]][0]
            type_counts[t_name] = type_counts.get(t_name, 0) + 1
        
        df_pie = pd.DataFrame(list(type_counts.items()), columns=["Type", "Count"])
        fig_pie = px.pie(
            df_pie,
            names="Type",
            values="Count",
            hole=0.62,
            color_discrete_sequence=['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#64748b']
        )
        fig_pie.update_layout(
            height=210,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # CHARTS ROW 2: Alerts & Distribution
    r1, r2 = st.columns([1, 1])
    with r1:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Recent Alerts</h3>", unsafe_allow_html=True)
        recent_alerts = open_alerts[:4]
        if recent_alerts:
            for a in recent_alerts:
                level_class = f"pill-{a['level']}"
                lvl_label = "CRITICAL" if a['level'] == 'cr' else ("WARN" if a['level'] == 'wa' else "INFO")
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid #f1f3f9;">
                        <span class="pill {level_class}">{lvl_label}</span>
                        <div style="flex:1;">
                            <div style="font-weight:600; font-size:13px; color:#0f172a;">{a['text']}</div>
                            <div style="font-size:12px; color:#64748b;">{a['site']} · {a['time']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No open alerts at this time.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Alerts by Interval</h3><span style='color:#64748b; font-size:13px;'>Hourly incident volume</span>", unsafe_allow_html=True)
        hours = [f"{h}:00" for h in range(8, 20)]
        vol = [random.randint(1, 9) for _ in hours]
        df_bars = pd.DataFrame({"Hour": hours, "Alerts": vol})
        fig_bars = px.bar(df_bars, x="Hour", y="Alerts", color_discrete_sequence=['#4f46e5'])
        fig_bars.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#e6e9f2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_bars, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. DEVICES
# ----------------------------------------------------
elif page == "Devices":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    # Filter Bar
    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search_query = st.text_input("Search", placeholder="Search by name, brand, or IP...", label_visibility="collapsed")
    with fc2:
        site_filter = st.selectbox("Warehouse", ["All Warehouses"] + SITES, label_visibility="collapsed")
    with fc3:
        type_options = ["All Types"] + [TYPES[k][0] for k in TYPES]
        type_filter = st.selectbox("Type", type_options, label_visibility="collapsed")
    with fc4:
        status_filter = st.selectbox("Status", ["All Statuses", "Online", "Warning", "Offline"], label_visibility="collapsed")

    # Filter logic
    filtered = []
    for d in st.session_state.devices:
        matches_query = not search_query or (
            search_query.lower() in d["name"].lower() or
            search_query.lower() in d["ip"] or
            search_query.lower() in d["brand"].lower()
        )
        matches_site = (site_filter == "All Warehouses") or (d["site"] == site_filter)
        t_label = TYPES[d["type"]][0]
        matches_type = (type_filter == "All Types") or (t_label == type_filter)
        st_map = {"Online": "on", "Warning": "warn", "Offline": "off"}
        matches_status = (status_filter == "All Statuses") or (d["status"] == st_map.get(status_filter))
        
        if matches_query and matches_site and matches_type and matches_status:
            filtered.append(d)

    st.write(f"Showing **{len(filtered)}** devices")

    # Interactive Table / Device Card List
    for dev in filtered:
        st_class = "pill-ok" if dev["status"] == "on" else ("pill-wa" if dev["status"] == "warn" else "pill-cr")
        st_label = "Online" if dev["status"] == "on" else ("Warning" if dev["status"] == "warn" else "Offline")
        icon = TYPES[dev["type"]][1]

        with st.expander(f"{icon} **{dev['name']}**  —  {dev['brand']} ({dev['site']})  |  Status: {st_label}"):
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                st.write(f"**IP Address:** `{dev['ip']}`")
                st.write(f"**OS / Firmware:** {dev['os']}")
                st.write(f"**Uptime:** {dev['uptime_days']} days")
            with dc2:
                st.write(f"**CPU Usage:** {dev['cpu']}%")
                st.progress(dev['cpu'] / 100)
                st.write(f"**Memory:** {dev['memory']}%")
                st.progress(dev['memory'] / 100)
            with dc3:
                st.write(f"**Signal Strength:** {dev['signal']}%")
                st.progress(dev['signal'] / 100)
                st.write(f"**Storage:** {dev['storage']}%")
                st.progress(dev['storage'] / 100)
            
            st.divider()
            bcol1, bcol2, bcol3, _ = st.columns([1, 1.2, 1, 3])
            with bcol1:
                if st.button("🔄 Restart", key=f"rst_{dev['id']}"):
                    st.toast(f"Restart command sent to {dev['name']}")
            with bcol2:
                if st.button("🧪 Diagnostics", key=f"diag_{dev['id']}"):
                    st.toast(f"Diagnostics running on {dev['name']}...")
            with bcol3:
                if st.button("❌ Disconnect", key=f"dc_{dev['id']}"):
                    dev["status"] = "off"
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CONNECT DEVICE
# ----------------------------------------------------
elif page == "Connect Device":
    c_left, c_right = st.columns([1.5, 1])
    
    with c_left:
        st.markdown("<div class='glass-card'><h2 style='font-size:18px; margin-top:0;'>Add a New Warehouse Device</h2>", unsafe_allow_html=True)
        with st.form("add_device_form", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                dev_type_key = st.selectbox(
                    "Device Type",
                    options=list(TYPES.keys()),
                    format_func=lambda k: f"{TYPES[k][1]} {TYPES[k][0]}"
                )
                conn_method = st.selectbox(
                    "Connection Method",
                    ["Auto-discover", "Install agent (One-liner)", "QR / Pairing code", "Manual IP / SNMP"]
                )
            with col_t2:
                site_choice = st.selectbox("Warehouse", SITES)
                dev_name = st.text_input("Device Name", placeholder="e.g. Packing Laptop 4")
            
            ip_addr = st.text_input("IP Address", placeholder="e.g. 192.168.10.125")
            submitted = st.form_submit_button("🚀 Connect Device", use_container_width=True)

            if submitted:
                new_name = dev_name.strip() or f"{TYPES[dev_type_key][0]} {len(st.session_state.devices) + 1}"
                new_ip = ip_addr.strip() or f"192.168.10.{random.randint(100, 250)}"
                st.session_state.devices.append({
                    "id": len(st.session_state.devices),
                    "name": new_name,
                    "type": dev_type_key,
                    "brand": "Configured",
                    "os": "Auto-detected",
                    "ip": new_ip,
                    "site_idx": SITES.index(site_choice),
                    "site": site_choice,
                    "status": "on",
                    "cpu": 25,
                    "memory": 40,
                    "storage": 35,
                    "signal": 95,
                    "uptime_days": 1
                })
                st.success(f"Device **{new_name}** ({new_ip}) successfully connected and synced!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='glass-card'><h3 style='margin-top:0; font-size:16px;'>Discovered on your network</h3><p style='color:#64748b; font-size:13px;'>Found by scanning Pune warehouse subnet</p>", unsafe_allow_html=True)
        if st.session_state.discovered:
            for idx, disc in enumerate(st.session_state.discovered):
                dcol1, dcol2 = st.columns([3, 1])
                with dcol1:
                    icon = TYPES[disc["type"]][1]
                    st.write(f"**{icon} {disc['name']}**")
                    st.caption(f"{disc['ip']} · {SITES[disc['site_idx']]}")
                with dcol2:
                    if st.button("Adopt", key=f"adopt_{idx}"):
                        st.session_state.devices.append({
                            "id": len(st.session_state.devices),
                            "name": disc["name"],
                            "type": disc["type"],
                            "brand": disc["brand"],
                            "os": "Auto-detected",
                            "ip": disc["ip"],
                            "site_idx": disc["site_idx"],
                            "site": SITES[disc["site_idx"]],
                            "status": "on",
                            "cpu": 30,
                            "memory": 45,
                            "storage": 20,
                            "signal": 88,
                            "uptime_days": 1
                        })
                        st.session_state.discovered.pop(idx)
                        st.toast(f"{disc['name']} adopted successfully!")
                        st.rerun()
                st.divider()
        else:
            st.info("Everything found on the network is already connected ✔")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. ALERTS
# ----------------------------------------------------
elif page == "Alerts":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    open_alerts = [a for a in st.session_state.alerts if not a["ack"]]
    if open_alerts:
        for alert in open_alerts:
            level_pill = f"pill-{alert['level']}"
            lvl_name = "CRITICAL" if alert['level'] == 'cr' else ("WARNING" if alert['level'] == 'wa' else "INFO")
            
            ac1, ac2 = st.columns([5, 1])
            with ac1:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span class="pill {level_pill}">{lvl_name}</span>
                        <div>
                            <div style="font-weight:700; font-size:14px; color:#0f172a;">{alert['text']}</div>
                            <div style="font-size:12px; color:#64748b;">{alert['site']}, Pune · {alert['time']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with ac2:
                if st.button("Acknowledge", key=f"ack_{alert['id']}"):
                    alert["ack"] = True
                    st.toast("Alert marked as acknowledged")
                    st.rerun()
            st.divider()
    else:
        st.success("🎉 No open alerts! All warehouse devices are functioning normally.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. WAREHOUSES
# ----------------------------------------------------
elif page == "Warehouses":
    cols = st.columns(3)
    for i, site_name in enumerate(SITES):
        with cols[i]:
            site_devs = [d for d in st.session_state.devices if d["site_idx"] == i]
            total_site = len(site_devs)
            online_site = len([d for d in site_devs if d["status"] == "on"])
            pct = round((online_site / total_site) * 100) if total_site else 100
            color = "#ef4444" if pct < 85 else ("#f59e0b" if pct < 95 else "#10b981")

            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <h3 style="margin:0; font-size:18px;">{site_name}</h3>
                        <span style="font-size:18px; font-weight:800; color:{color};">{pct}%</span>
                    </div>
                    <div style="font-size:13px; color:#64748b; margin-bottom:14px;">
                        Pune · <b>{total_site}</b> devices · {total_site - online_site} need attention
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(pct / 100)
            
            # Type summary chips
            type_tallies = {}
            for d in site_devs:
                t_key = d["type"]
                type_tallies[t_key] = type_tallies.get(t_key, 0) + 1
            
            chips_html = " ".join([f"<span class='pill pill-in' style='margin:2px;'>{TYPES[k][1]} {type_tallies[k]}</span>" for k in type_tallies])
            st.markdown(f"<div style='margin-top:14px;'>{chips_html}</div></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 6. REPORTS
# ----------------------------------------------------
elif page == "Reports":
    col_rep1, col_rep2 = st.columns([1, 1])
    with col_rep1:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Weekly Uptime Trend</h3><span style='color:#64748b; font-size:13px;'>Average across all 3 Pune facilities</span>", unsafe_allow_html=True)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        vals = [98.2, 97.9, 98.8, 96.4, 97.7, 98.9, 99.1]
        fig_week = px.line(x=days, y=vals, markers=True, color_discrete_sequence=['#10b981'])
        fig_week.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(title=None, showgrid=False),
            yaxis=dict(title=None, range=[95, 100], gridcolor='#e6e9f2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_week, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_rep2:
        st.markdown("<div class='glass-card'><h3 style='margin:0 0 4px 0; font-size:16px;'>Downtime by Device Type</h3><span style='color:#64748b; font-size:13px;'>Hours lost this month</span>", unsafe_allow_html=True)
        d_types = ["Scanners", "Routers", "Printers", "CCTV", "Monitors"]
        d_hours = [14, 9, 7, 5, 3]
        fig_dt = px.bar(x=d_hours, y=d_types, orientation='h', color_discrete_sequence=['#4f46e5'])
        fig_dt.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(title=None, gridcolor='#e6e9f2'),
            yaxis=dict(title=None, showgrid=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_dt, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3 Summary Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("""
        <div class="kpi-container">
            <div>
                <div class="kpi-title">Avg Repair Time</div>
                <div class="kpi-value">18 min</div>
                <div class="kpi-sub" style="color:#10b981;">▼ 4 min vs last week</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="kpi-container">
            <div>
                <div class="kpi-title">Alerts Resolved</div>
                <div class="kpi-value">92%</div>
                <div class="kpi-sub" style="color:#10b981;">▲ 5% vs last week</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="kpi-container">
            <div>
                <div class="kpi-title">Devices At Risk</div>
                <div class="kpi-value">3</div>
                <div class="kpi-sub" style="color:#f59e0b;">firmware outdated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
