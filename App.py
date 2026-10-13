import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DMFR Automations Control Room",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR EXACT BLUE PRISM / MODERN UI STYLING ---
st.markdown("""
<style>
    /* Global Background and font adjustments */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Top Header Running Tag */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .top-title {
        font-size: 26px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .running-badge {
        background-color: #dcfce7;
        color: #15803d;
        font-size: 13px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 14px;
        border: 1px solid #86efac;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Pulsing Live Banner */
    .pulsing-banner {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #166534;
        font-weight: 600;
        font-size: 14px;
    }
    .pulse-dot {
        height: 10px;
        width: 10px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse 1.6s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* Metric KPI Cards */
    .metric-card {
        border-radius: 10px;
        padding: 16px 20px;
        border: 1.5px solid;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title {
        font-size: 14px;
        font-weight: 600;
        color: #475569;
    }
    .metric-val {
        font-size: 32px;
        font-weight: 700;
        line-height: 1;
    }
    .metric-sub {
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
    }

    /* Status Pills */
    .badge-locked {
        background-color: #fef3c7;
        color: #b45309;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #fde68a;
        display: inline-block;
    }
    .badge-pending {
        background-color: #e0f2fe;
        color: #0369a1;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #bae6fd;
        display: inline-block;
    }
    .badge-completed {
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #bbf7d0;
        display: inline-block;
    }
    .badge-exception {
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #fecaca;
        display: inline-block;
    }

    /* Floating Event Log at Bottom Right */
    .event-log-container {
        position: fixed;
        bottom: 20px;
        right: 25px;
        width: 380px;
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        padding: 12px 16px;
        z-index: 9999;
        font-size: 12px;
    }
    .log-header {
        font-weight: 700;
        color: #1e293b;
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 4px;
    }
    .log-entry {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        color: #334155;
    }
    .log-highlight {
        background-color: #fef9c3;
        padding: 2px 4px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)


# --- MOCK DATA / SQL DATA FETCH HELPER ---
# Note: You can replace this with pyodbc.connect(...) to your DMFR_Automations DB!
def get_queue_data(process_name):
    if process_name == "Insurance Certificate Management (ICM)":
        return {
            "table_name": "Queue_ICM_Bot",
            "pending": 14,
            "locked": 2,
            "completed": 84,
            "exceptions": 5,
            "progress": 72,
            "worker_status": "PULSING: PERFORMER BOT: ACTIVE & PROCESSING",
            "items": [
                {"id": 105, "key": "TTU_ICM_20261013_091844", "status": "LOCKED", "worker": "RTR-BOT-01", "attempts": 1, "updated": "09:23:14 AM", "notes": ""},
                {"id": 106, "key": "TTU_ICM_20261013_091855", "status": "PENDING", "worker": "-", "attempts": 0, "updated": "09:18:55 AM", "notes": ""},
                {"id": 104, "key": "TTU_ICM_20261013_084511", "status": "COMPLETED", "worker": "RTR-BOT-02", "attempts": 1, "updated": "09:15:20 AM", "notes": ""},
                {"id": 103, "key": "TTU_ICM_20261013_081210", "status": "EXCEPTION", "worker": "RTR-BOT-01", "attempts": "3 (MAXED)", "updated": "08:42:01 AM", "notes": "System Error: Network folder missing"},
            ]
        }
    else:  # Chapter 2261
        return {
            "table_name": "Queue_Chapter2261_Reports",
            "pending": 1,
            "locked": 0,
            "completed": 12,
            "exceptions": 0,
            "progress": 100,
            "worker_status": "IDLE: AWAITING NEXT SCHEDULED RUN",
            "items": [
                {"id": 201, "key": "October_01_20261001_080000", "status": "COMPLETED", "worker": "RTR-BOT-01", "attempts": 1, "updated": "08:05:12 AM", "notes": "Email sent successfully"},
                {"id": 202, "key": "November_01_20261101_080000", "status": "PENDING", "worker": "-", "attempts": 0, "updated": "10:00:00 AM", "notes": "Scheduled for Nov 1"}
            ]
        }

# --- SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    st.markdown("### 🔷 DMFR Automations")
    st.markdown("<p style='color:#94a3b8; font-size:12px; margin-top:-10px;'>ENTERPRISE CONTROL ROOM</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**Menu Selection**")
    automation_choice = st.radio(
        label="Select Automation Script",
        options=[
            "Insurance Certificate Management (ICM)",
            "Chapter 2261 Reporting"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Active Session Indicator
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span class='pulse-dot' style='height:8px; width:8px; background-color:#22c55e;'></span>
            <span style='font-size: 13px; font-weight:600; color:#334155;'>Active Session</span>
        </div>
        <p style='font-size: 12px; color: #64748b; margin-top: 4px; margin-left: 16px;'>
            <b>3 Concurrent Users Online</b><br>
            (Admin, Developer 1, Manager S)
        </p>
    """, unsafe_allow_html=True)

# Fetch Data for Selected Automation
data = get_queue_data(automation_choice)

# --- MAIN CONTENT AREA ---

# 1. Top Header
st.markdown(f"""
    <div class='top-header'>
        <div class='top-title'>{automation_choice} Control Room</div>
        <div class='running-badge'>● RUNNING</div>
    </div>
""", unsafe_allow_html=True)

# 2. Live Pulsing Progress Banner
st.markdown(f"""
    <div class='pulsing-banner'>
        <div>
            <span class='pulse-dot'></span>&nbsp;&nbsp;
            <span>{data['worker_status']}</span>
        </div>
        <div>Live progress: {data['progress']}% &nbsp;&nbsp; <span style='cursor:pointer;'>✕</span></div>
    </div>
""", unsafe_allow_html=True)
st.progress(data['progress'] / 100)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 3. KPI Metric Cards (4 Columns)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='metric-card' style='border-color: #bfdbfe;'>
            <div class='metric-title'>Pending Items</div>
            <div class='metric-val' style='color: #0284c7;'>{data['pending']}</div>
            <div class='metric-sub'>To Be Processed</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card' style='border-color: #fde68a;'>
            <div class='metric-title'>Locked Items</div>
            <div class='metric-val' style='color: #d97706;'>{data['locked']}</div>
            <div class='metric-sub'>Processing on RTR</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card' style='border-color: #bbf7d0;'>
            <div class='metric-title'>Completed Today</div>
            <div class='metric-val' style='color: #16a34a;'>{data['completed']}</div>
            <div class='metric-sub'>+12 this hour</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='metric-card' style='border-color: #fecaca;'>
            <div class='metric-title'>Exceptions</div>
            <div class='metric-val' style='color: #dc2626;'>{data['exceptions']}</div>
            <div class='metric-sub'>Requires Review</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# 4. Real-Time Transaction Queue Table
st.markdown(f"#### Real-Time Transaction Queue - `{data['table_name']}` 📊")

# Table Header
h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7 = st.columns([1.2, 2.5, 1.3, 1.2, 1.0, 2.2, 1.8])
h_col1.caption("**Transaction ID**")
h_col2.caption("**Business Key**")
h_col3.caption("**Status**")
h_col4.caption("**Worker**")
h_col5.caption("**Attempts**")
h_col6.caption("**Last Updated**")
h_col7.caption("**Actions**")

st.markdown("<hr style='margin-top:0px; margin-bottom:8px;'>", unsafe_allow_html=True)

# Render Table Rows matching the image layout
for item in data['items']:
    r1, r2, r3, r4, r5, r6, r7 = st.columns([1.2, 2.5, 1.3, 1.2, 1.0, 2.2, 1.8])
    
    r1.write(f"**{item['id']}**")
    r2.write(f"`{item['key']}`")
    
    # Status badges
    if item['status'] == 'LOCKED':
        r3.markdown("<span class='badge-locked'>LOCKED ⏳</span>", unsafe_allow_html=True)
    elif item['status'] == 'PENDING':
        r3.markdown("<span class='badge-pending'>PENDING</span>", unsafe_allow_html=True)
    elif item['status'] == 'COMPLETED':
        r3.markdown("<span class='badge-completed'>COMPLETED</span>", unsafe_allow_html=True)
    elif item['status'] == 'EXCEPTION':
        r3.markdown("<span class='badge-exception'>EXCEPTION</span>", unsafe_allow_html=True)
        
    r4.write(item['worker'])
    
    # Attempts column
    if "MAXED" in str(item['attempts']):
        r5.markdown(f"<span style='color:#dc2626; font-weight:600;'>{item['attempts']}</span>", unsafe_allow_html=True)
    else:
        r5.write(str(item['attempts']))
        
    # Last updated & error note
    if item['notes']:
        r6.markdown(f"<div>{item['updated']}<br><span style='color:#dc2626; font-size:11px;'>{item['notes']}</span></div>", unsafe_allow_html=True)
    else:
        r6.write(item['updated'])
        
    # Interactive Actions
    with r7:
        if item['status'] == 'PENDING':
            if st.button("Trigger Now", key=f"trig_{item['id']}"):
                st.toast(f"Dispatched {item['id']} to Prefect Worker!")
        elif item['status'] == 'COMPLETED':
            st.button("📄", key=f"view_{item['id']}", help="View PDF Output")
        elif item['status'] == 'EXCEPTION':
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Retry", key=f"ret_{item['id']}"):
                    st.toast(f"Item {item['id']} reset to PENDING.")
            with btn_col2:
                if st.button("Release", key=f"rel_{item['id']}"):
                    st.toast(f"Stale lock released for {item['id']}.")

    st.markdown("<hr style='margin: 4px 0px; border-color: #f1f5f9;'>", unsafe_allow_html=True)


# --- 5. FLOATING SYSTEM EVENT LOG (Bottom-Right Widget) ---
st.markdown("""
    <div class='event-log-container'>
        <div class='log-header'>
            <span>Recent System Event Log</span>
            <span style='cursor:pointer;'>✕</span>
        </div>
        <div class='log-entry'>
            <span>Dispatcher: Inserted 18 pending items</span>
            <span style='color:#64748b;'>09:15:00 AM</span>
        </div>
        <div class='log-entry'>
            <span>Performer: Item 104 completed</span>
            <span style='color:#64748b;'>09:15:00 AM</span>
        </div>
        <div class='log-entry'>
            <span class='log-highlight'>STALE LOCK WATCHDOG: sp_DMFR_RequeueAllStaleLocks executed</span>
            <span style='color:#64748b;'>09:15:00 AM</span>
        </div>
    </div>
""", unsafe_allow_html=True)