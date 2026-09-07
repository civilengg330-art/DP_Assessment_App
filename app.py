import streamlit as st
import sqlite3
import pandas as pd

# Master Passcode for DP Coordinator
COORDINATOR_PASSCODE = "cust123"

def init_and_get_connection():
    conn = sqlite3.connect("dp_assessment_v2.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supervisor_name TEXT NOT NULL,
            group_number TEXT NOT NULL,
            dp_part TEXT NOT NULL,
            report_number TEXT NOT NULL,
            s1_name TEXT NOT NULL,
            s1_raw INTEGER NOT NULL,
            s1_weighted REAL NOT NULL,
            s2_name TEXT NOT NULL,
            s2_raw INTEGER NOT NULL,
            s2_weighted REAL NOT NULL,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_number, dp_part, report_number)
        )
    """)
    
    new_cols = [
        ("s1_clo1", "INTEGER"), ("s1_clo2", "INTEGER"), ("s1_clo3", "INTEGER"), ("s1_clo4", "INTEGER"),
        ("s2_clo1", "INTEGER"), ("s2_clo2", "INTEGER"), ("s2_clo3", "INTEGER"), ("s2_clo4", "INTEGER")
    ]
    cursor.execute("PRAGMA table_info(evaluations)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {col_name} {col_type}")
            
    conn.commit()
    return conn

# Criteria grouped by CLO based on CUST DP-II Form
CLO_STRUCTURE = {
    "CLO 1": [
        ("CLO 1 (a)", "Integrated solution for a real-world problem"),
        ("CLO 1 (b)", "Development of solution using modern tools"),
        ("CLO 1 (c)", "Establish a feasible output (patent, etc.)")
    ],
    "CLO 2": [
        ("CLO 2 (a)", "Methodical reporting of project work"),
        ("CLO 2 (b)", "Investigation and analysis of project tasks"),
        ("CLO 2 (c)", "Appraising of the project outcomes")
    ],
    "CLO 3": [
        ("CLO 3 (a)", "Formulating project output through effective communication"),
        ("CLO 3 (b)", "Reconciling SDG relevance through specialized topic clarity"),
        ("CLO 3 (c)", "Mastering of modern tools for results and analysis")
    ],
    "CLO 4": [
        ("CLO 4 (a)", "Coordinating realistic limitations and considerations"),
        ("CLO 4 (b)", "Building clarity of project output"),
        ("CLO 4 (c)", "Meeting varying requirements for commercialized use")
    ]
}

GROUPS = [f"Group-{i+1:02d}" for i in range(25)]

st.set_page_config(page_title="DP Assessment Portal", layout="wide")

st.sidebar.title("Navigation")
role = st.sidebar.radio("Select Portal Role:", ["Supervisor Evaluation Form", "DP Coordinator Master Portal"])

# --- 1. SUPERVISOR PORTAL ---
if role == "Supervisor Evaluation Form":
    st.title("📋 DP Progress Evaluation Form")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sup_name = st.text_input("Supervisor Name", value="", placeholder="Enter your full name")
    with col2:
        group_no = st.selectbox("Group Number", GROUPS)
    with col3:
        dp_part = st.selectbox("DP Part", ["DP Part-1", "DP Part-2"])
    with col4:
        report_no = st.selectbox("Report Number", ["Report 1 (5%)", "Report 2 (10%)", "Report 3 (10%)"])

    st.subheader("Student Details")
    sc1, sc2 = st.columns(2)
    with sc1:
        s1_name = st.text_input("Student 1 Name/ID", value="Student A")
    with sc2:
        s2_name = st.text_input("Student 2 Name/ID", value="Student B")

    st.subheader("Evaluation Matrix (Performance Levels: 0, 1, 2, 3)")
    
    s1_clo_scores = {"CLO 1": 0, "CLO 2": 0, "CLO 3": 0, "CLO 4": 0}
    s2_clo_scores = {"CLO 1": 0, "CLO 2": 0, "CLO 3": 0, "CLO 4": 0}

    for clo_name, sub_criteria in CLO_STRUCTURE.items():
        st.markdown(f"### {clo_name} (Out of 9)")
        for code, desc in sub_criteria:
            st.markdown(f"**{code}:** {desc}")
            c1, c2 = st.columns(2)
            with c1:
                sc1_val = st.selectbox(f"{s1_name} - {code}", [0, 1, 2, 3], key=f"s1_{code}")
                s1_clo_scores[clo_name] += sc1_val
            with c2:
                sc2_val = st.selectbox(f"{s2_name} - {code}", [0, 1, 2, 3], key=f"s2_{code}")
                s2_clo_scores[clo_name] += sc2_val
        st.divider()

    # Automatic Score Calculations
    s1_raw = sum(s1_clo_scores.values())
    s2_raw = sum(s2_clo_scores.values())
    weight_factor = 0.05 if "Report 1" in report_no else 0.10
    
    s1_weighted = round((s1_raw / 36.0) * (weight_factor * 100), 2)
    s2_weighted = round((s2_raw / 36.0) * (weight_factor * 100), 2)

    st.info(f"**Calculated Score Summary ({report_no}):**\n"
            f"* **{s1_name}:** CLO1: {s1_clo_scores['CLO 1']}/9 | CLO2: {s1_clo_scores['CLO 2']}/9 | CLO3: {s1_clo_scores['CLO 3']}/9 | CLO4: {s1_clo_scores['CLO 4']}/9 ➔ **Raw Total:** {s1_raw}/36 | **Weighted:** {s1_weighted}%\n"
            f"* **{s2_name}:** CLO1: {s2_clo_scores['CLO 1']}/9 | CLO2: {s2_clo_scores['CLO 2']}/9 | CLO3: {s2_clo_scores['CLO 3']}/9 | CLO4: {s2_clo_scores['CLO 4']}/9 ➔ **Raw Total:** {s2_raw}/36 | **Weighted:** {s2_weighted}%")

    if st.button("Submit / Update Evaluation", type="primary"):
        if not sup_name.strip():
            st.error("Please enter Supervisor Name before submitting.")
        else:
            conn = init_and_get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO evaluations 
                    (supervisor_name, group_number, dp_part, report_number, 
                     s1_name, s1_clo1, s1_clo2, s1_clo3, s1_clo4, s1_raw, s1_weighted, 
                     s2_name, s2_clo1, s2_clo2, s2_clo3, s2_clo4, s2_raw, s2_weighted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (sup_name.strip(), group_no, dp_part, report_no, 
                      s1_name, s1_clo_scores['CLO 1'], s1_clo_scores['CLO 2'], s1_clo_scores['CLO 3'], s1_clo_scores['CLO 4'], s1_raw, s1_weighted,
                      s2_name, s2_clo_scores['CLO 1'], s2_clo_scores['CLO 2'], s2_clo_scores['CLO 3'], s2_clo_scores['CLO 4'], s2_raw, s2_weighted))
                conn.commit()
                st.success(f"Evaluation for {group_no} ({report_no}) saved/updated successfully!")
            except Exception as e:
                st.error(f"Error saving data: {e}")
            finally:
                conn.close()

    # --- SUPERVISOR GROUP PROGRESS SUMMARY BELOW FORM (FILTERED) ---
    st.markdown("---")
    st.subheader(f"📊 Progress Summary for {group_no}")
    
    if sup_name.strip():
        conn = init_and_get_connection()
        summary_df = pd.read_sql_query(
            """SELECT dp_part, report_number, s1_name, s1_clo1, s1_clo2, s1_clo3, s1_clo4, s1_raw, s1_weighted, 
                      s2_name, s2_clo1, s2_clo2, s2_clo3, s2_clo4, s2_raw, s2_weighted 
               FROM evaluations 
               WHERE group_number = ? AND supervisor_name = ?""", 
            conn, params=(group_no, sup_name.strip())
        )
        conn.close()

        if summary_df.empty:
            st.caption(f"No previous reports submitted by {sup_name.strip()} for {group_no} yet.")
        else:
            st.dataframe(summary_df, use_container_width=True)
    else:
        st.caption("Please enter your Supervisor Name above to view your previous submissions for this group.")

# --- 2. DP COORDINATOR PORTAL (PASSCODE PROTECTED) ---
elif role == "DP Coordinator Master Portal":
    st.title("🎓 DP Coordinator Master Dashboard")
    
    with st.sidebar.form("login_form"):
        passcode = st.text_input("Enter Coordinator Passcode:", type="password")
        submit_passcode = st.form_submit_button("Access Master Portal")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if submit_passcode:
        if passcode == COORDINATOR_PASSCODE:
            st.session_state.authenticated = True
        else:
            st.session_state.authenticated = False
            st.sidebar.error("Incorrect passcode.")

    if st.session_state.authenticated:
        st.success("Access Granted")
        
        conn = init_and_get_connection()
        df = pd.read_sql_query("SELECT * FROM evaluations", conn)
        conn.close()

        if df.empty:
            st.warning("No supervisor evaluations submitted yet.")
        else:
            st.subheader("Master Assessment Records (All Groups & Supervisors)")
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Master Excel/CSV File",
                data=csv_data,
                file_name="DP_Master_Assessment_Data.csv",
                mime="text/csv"
            )
    else:
        st.info("Please enter the Coordinator Passcode in the sidebar and click 'Access Master Portal'.")
