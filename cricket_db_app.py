"""
Cricket Database Management System - Streamlit Frontend
Final Clean Version - All Errors Fixed
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date
import hashlib


# Page configuration
st.set_page_config(
    page_title="Cricket DB Manager",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)


# DATABASE CONNECTION
def init_connection():
    """Initialize MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return connection
    except Error as e:
        st.error(f"Database Connection Error: {str(e)}")
        return None


# AUTHENTICATION
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username, password):
    """Authenticate user"""
    if not username or not password:
        return None

    conn = init_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        hashed_pw = hash_password(password)

        cursor.execute(
            "SELECT user_id, username, role FROM users WHERE username = %s AND password = %s",
            (username, hashed_pw)
        )
        user = cursor.fetchone()
        cursor.close()
        return user
    except Error as e:
        st.error(f"Authentication Error: {str(e)}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()


# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0


# LOGIN PAGE
def login_page():
    """Display login page"""
    st.title("🏏 Cricket Database Manager")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("Login")

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("🔓 Login", use_container_width=True):
                if st.session_state.login_attempts >= 5:
                    st.error("Too many login attempts. Please try again later.")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = user['username']
                        st.session_state.role = user['role']
                        st.session_state.login_attempts = 0
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"Invalid credentials. Attempts: {st.session_state.login_attempts}/5")

        with col_btn2:
            if st.button("❓ Help", use_container_width=True):
                st.info("""
                **Demo Credentials:**
                - Admin: admin / admin123
                - User: user / user123
                """)

        st.markdown("---")
        st.info("""
        **Demo Credentials:**

        **Admin Account** (Full Access):
        - Username: admin
        - Password: admin123

        **User Account** (Read-Only):
        - Username: user
        - Password: user123
        """)


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


# EXECUTE QUERY
def execute_query(query, params=None, fetch=False):
    """Execute SQL query with proper error handling"""
    conn = init_connection()
    if not conn:
        return [] if fetch else False

    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()
            return result if result else []
        else:
            conn.commit()
            return True
    except Error as e:
        st.error(f"Query Error: {str(e)}")
        return [] if fetch else False
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()


# CRUD OPERATIONS - CREATE
def create_player():
    """Create new player"""
    st.subheader("➕ Add New Player")

    with st.form(key="create_player_form"):
        col1, col2 = st.columns(2)

        with col1:
            player_id = st.number_input("Player ID", min_value=1, step=1)
            f_name = st.text_input("First Name")
            l_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())

        with col2:
            teams = execute_query("SELECT team_id, team_name FROM team ORDER BY team_name", fetch=True)
            team_options = {t['team_name']: t['team_id'] for t in teams} if teams else {}

            if not team_options:
                st.error("No teams available")
                return

            selected_team = st.selectbox("Team", options=list(team_options.keys()))

            roles = execute_query("SELECT role_id, role_name FROM role ORDER BY role_name", fetch=True)
            role_options = {r['role_name']: r['role_id'] for r in roles} if roles else {}

            if not role_options:
                st.error("No roles available")
                return

            selected_role = st.selectbox("Role", options=list(role_options.keys()))

        submitted = st.form_submit_button("✅ Add Player", use_container_width=True)

        if submitted:
            if not f_name or not l_name:
                st.error("Please fill all fields")
            else:
                existing = execute_query(
                    "SELECT player_id FROM player WHERE player_id = %s",
                    (player_id,),
                    fetch=True
                )

                if existing:
                    st.error(f"Player with ID {player_id} already exists")
                else:
                    query = """INSERT INTO player (player_id, f_name, l_name, dob, team_id, role_id) 
                              VALUES (%s, %s, %s, %s, %s, %s)"""
                    params = (player_id, f_name, l_name, dob, 
                             team_options[selected_team], role_options[selected_role])

                    if execute_query(query, params):
                        st.success(f"Player {f_name} {l_name} added successfully!")
                    else:
                        st.error("Failed to add player")


# CRUD OPERATIONS - READ
def read_players():
    """Display all players with filters and sorting"""
    st.subheader("👥 View Players")

    teams = execute_query("SELECT DISTINCT team_name FROM team ORDER BY team_name", fetch=True)
    team_list = [t['team_name'] for t in teams] if teams else []

    roles = execute_query("SELECT DISTINCT role_name FROM role ORDER BY role_name", fetch=True)
    role_list = [r['role_name'] for r in roles] if roles else []

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_teams = st.multiselect("Filter by Team", options=team_list, key="filter_team")

    with col2:
        selected_roles = st.multiselect("Filter by Role", options=role_list, key="filter_role")

    with col3:
        sort_by = st.selectbox("Sort By", options=["Player ID", "First Name", "Age", "Team"])

    query = """
    SELECT p.player_id, p.f_name, p.l_name,
           p.dob, p.age, t.team_name, r.role_name
    FROM player p
    JOIN team t ON p.team_id = t.team_id
    JOIN role r ON p.role_id = r.role_id
    ORDER BY p.player_id
    """

    players = execute_query(query, fetch=True)

    if players:
        df = pd.DataFrame(players)

        if selected_teams:
            df = df[df['team_name'].isin(selected_teams)]

        if selected_roles:
            df = df[df['role_name'].isin(selected_roles)]

        if sort_by == "Player ID":
            df = df.sort_values('player_id')
        elif sort_by == "First Name":
            df = df.sort_values('f_name')
        elif sort_by == "Age":
            df = df.sort_values('age', ascending=False)
        elif sort_by == "Team":
            df = df.sort_values('team_name')

        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Players", len(df))
        with col2:
            st.metric("Teams", df['team_name'].nunique())
        with col3:
            st.metric("Roles", df['role_name'].nunique())
        with col4:
            st.metric("Avg Age", int(df['age'].mean()) if len(df) > 0 else 0)
    else:
        st.info("No players found")


# CRUD OPERATIONS - UPDATE
def update_player():
    """Update player information"""
    st.subheader("✏️ Update Player")

    players = execute_query(
        "SELECT player_id, CONCAT(f_name, ' ', l_name) as name FROM player ORDER BY player_id",
        fetch=True
    )

    if not players:
        st.info("No players available")
        return

    player_options = {f"{p['name']} (ID: {p['player_id']})" : p['player_id'] for p in players}
    selected = st.selectbox("Select Player", options=list(player_options.keys()))
    player_id = player_options[selected]

    current_data = execute_query(
        "SELECT * FROM player WHERE player_id = %s",
        (player_id,),
        fetch=True
    )

    if not current_data:
        st.error("Player not found")
        return

    current = current_data[0]

    with st.form(key="update_player_form"):
        col1, col2 = st.columns(2)

        with col1:
            f_name = st.text_input("First Name", value=current['f_name'])
            l_name = st.text_input("Last Name", value=current['l_name'])

        with col2:
            teams = execute_query("SELECT team_id, team_name FROM team ORDER BY team_name", fetch=True)
            team_options = {t['team_name']: t['team_id'] for t in teams} if teams else {}

            if current['team_id'] in [v for v in team_options.values()]:
                current_team = [k for k, v in team_options.items() if v == current['team_id']][0]
                selected_team = st.selectbox("Team", options=list(team_options.keys()),
                                            index=list(team_options.keys()).index(current_team))
            else:
                selected_team = st.selectbox("Team", options=list(team_options.keys()))

            roles = execute_query("SELECT role_id, role_name FROM role ORDER BY role_name", fetch=True)
            role_options = {r['role_name']: r['role_id'] for r in roles} if roles else {}

            if current['role_id'] in [v for v in role_options.values()]:
                current_role = [k for k, v in role_options.items() if v == current['role_id']][0]
                selected_role = st.selectbox("Role", options=list(role_options.keys()),
                                            index=list(role_options.keys()).index(current_role))
            else:
                selected_role = st.selectbox("Role", options=list(role_options.keys()))

        submitted = st.form_submit_button("💾 Update Player", use_container_width=True)

        if submitted:
            query = """UPDATE player 
                      SET f_name = %s, l_name = %s, team_id = %s, role_id = %s 
                      WHERE player_id = %s"""
            params = (f_name, l_name, team_options[selected_team], 
                     role_options[selected_role], player_id)

            if execute_query(query, params):
                st.success("Player updated successfully!")
            else:
                st.error("Failed to update player")


# CRUD OPERATIONS - DELETE
def delete_player():
    """Delete player"""
    st.subheader("🗑️ Delete Player")

    players = execute_query(
        "SELECT player_id, CONCAT(f_name, ' ', l_name) as name FROM player ORDER BY player_id",
        fetch=True
    )

    if not players:
        st.info("No players available")
        return

    player_options = {f"{p['name']} (ID: {p['player_id']})" : p['player_id'] for p in players}
    selected = st.selectbox("Select Player to Delete", options=list(player_options.keys()))
    player_id = player_options[selected]

    st.warning(f"⚠️ WARNING: Deleting {selected}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Confirm Delete", use_container_width=True):
            try:
                execute_query("DELETE FROM player_performance WHERE player_id = %s", (player_id,))
                execute_query("DELETE FROM award WHERE player_id = %s", (player_id,))

                if execute_query("DELETE FROM player WHERE player_id = %s", (player_id,)):
                    st.success("Player deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete player")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col2:
        if st.button("↩️ Cancel", use_container_width=True):
            st.info("Delete cancelled")


# UPDATE MATCH DETAILS
def update_match():
    """Update match details"""
    st.subheader("✏️ Update Match Details")

    matches = execute_query(
        """SELECT m.match_id, CONCAT('Match ', m.match_id, ': ', t1.team_name, ' vs ', t2.team_name, ' on ', m.date_of_match) as name 
           FROM matches m
           JOIN team t1 ON m.winning_team_id = t1.team_id
           JOIN team t2 ON m.losing_team_id = t2.team_id
           ORDER BY m.date_of_match DESC""", fetch=True)

    if not matches:
        st.info("No matches available")
        return

    match_options = {m['name']: m['match_id'] for m in matches}
    selected = st.selectbox("Select Match", options=list(match_options.keys()), key="match_select")
    match_id = match_options[selected]

    current_data = execute_query(
        "SELECT * FROM matches WHERE match_id = %s", (match_id,), fetch=True)

    if not current_data:
        st.error("Match not found")
        return

    current = current_data[0]

    teams = execute_query("SELECT team_id, team_name FROM team ORDER BY team_name", fetch=True)
    team_options = {t['team_name']: t['team_id'] for t in teams} if teams else {}

    tournaments = execute_query("SELECT tournament_id, tournament_name FROM tournament ORDER BY tournament_name", fetch=True)
    tournament_options = {t['tournament_name']: t['tournament_id'] for t in tournaments} if tournaments else {}

    with st.form(key="update_match_form"):
        col1, col2 = st.columns(2)

        with col1:
            winning_team_name = [k for k, v in team_options.items() if v == current['winning_team_id']][0]
            winning_team = st.selectbox("Winning Team", list(team_options.keys()), 
                                       index=list(team_options.keys()).index(winning_team_name), key="win_team")
            
            losing_team_name = [k for k, v in team_options.items() if v == current['losing_team_id']][0]
            losing_team = st.selectbox("Losing Team", list(team_options.keys()),
                                      index=list(team_options.keys()).index(losing_team_name), key="lose_team")

        with col2:
            date_of_match = st.date_input("Match Date", value=current['date_of_match'], key="match_date")
            location = st.text_input("Location", value=current['location'], key="match_location")

        tournament_name = [k for k, v in tournament_options.items() if v == current['tournament_id']][0]
        tournament = st.selectbox("Tournament", list(tournament_options.keys()),
                                 index=list(tournament_options.keys()).index(tournament_name), key="tournament")

        submitted = st.form_submit_button("💾 Update Match", use_container_width=True)

        if submitted:
            query = """UPDATE matches SET winning_team_id = %s, losing_team_id = %s, date_of_match = %s,
                       location = %s, tournament_id = %s WHERE match_id = %s"""
            params = (team_options[winning_team], team_options[losing_team], date_of_match, 
                     location, tournament_options[tournament], match_id)
            if execute_query(query, params):
                st.success("Match updated successfully!")
            else:
                st.error("Failed to update match")


# UPDATE PLAYER PERFORMANCE
# UPDATE PLAYER PERFORMANCE (WITH TEAM FILTERING & SORTING)
def update_player_performance():
    """Update player performance stats with team and player filtering"""
    st.subheader("✏️ Update Player Performance & Scores")

    # Get all teams for filtering
    teams = execute_query("SELECT DISTINCT team_id, team_name FROM team ORDER BY team_name", fetch=True)
    team_list = [t['team_name'] for t in teams] if teams else []

    col1, col2 = st.columns(2)

    with col1:
        selected_team = st.selectbox("Filter by Team", options=["All Teams"] + team_list, key="perf_team_filter")

    with col2:
        sort_by = st.selectbox("Sort By", options=["Player Name", "Runs Scored", "Wickets Taken"], key="perf_sort")

    # Build query based on selected team
    if selected_team == "All Teams":
        query = """
        SELECT pp.performance_id, pp.player_id, pp.match_id, pp.runs_scored, pp.wickets_taken,
               CONCAT(p.f_name, ' ', p.l_name) as player_name,
               t.team_name,
               CONCAT(p.f_name, ' ', p.l_name, ' (', t.team_name, ') - Match ', m.match_id) as full_name
        FROM player_performance pp
        JOIN player p ON pp.player_id = p.player_id
        JOIN team t ON p.team_id = t.team_id
        JOIN matches m ON pp.match_id = m.match_id
        ORDER BY m.date_of_match DESC
        """
        performances = execute_query(query, fetch=True)
    else:
        query = """
        SELECT pp.performance_id, pp.player_id, pp.match_id, pp.runs_scored, pp.wickets_taken,
               CONCAT(p.f_name, ' ', p.l_name) as player_name,
               t.team_name,
               CONCAT(p.f_name, ' ', p.l_name, ' (', t.team_name, ') - Match ', m.match_id) as full_name
        FROM player_performance pp
        JOIN player p ON pp.player_id = p.player_id
        JOIN team t ON p.team_id = t.team_id
        JOIN matches m ON pp.match_id = m.match_id
        WHERE t.team_name = %s
        ORDER BY m.date_of_match DESC
        """
        performances = execute_query(query, (selected_team,), fetch=True)

    if not performances:
        st.info("No player performances available for selected team")
        return

    # Convert to dataframe for sorting
    df = pd.DataFrame(performances)

    # Apply sorting
    if sort_by == "Player Name":
        df = df.sort_values('player_name')
    elif sort_by == "Runs Scored":
        df = df.sort_values('runs_scored', ascending=False)
    elif sort_by == "Wickets Taken":
        df = df.sort_values('wickets_taken', ascending=False)

    # Display performances table
    st.markdown("---")
    st.subheader(f"📊 Available Performances ({len(df)} records)")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Player (Team)**")
    with col2:
        st.write("**Runs**")
    with col3:
        st.write("**Wickets**")
    
    st.markdown("---")

    # Display with simple selection
    performance_options = {row['full_name']: row['performance_id'] for _, row in df.iterrows()}
    
    selected = st.selectbox("Select Performance Record to Update", 
                           options=list(performance_options.keys()), 
                           key="perf_select_sorted")
    performance_id = performance_options[selected]

    current_data = execute_query(
        "SELECT * FROM player_performance WHERE performance_id = %s", (performance_id,), fetch=True)

    if not current_data:
        st.error("Performance record not found")
        return

    current = current_data[0]

    st.markdown("---")
    st.subheader("📝 Update Performance Details")

    with st.form(key="update_performance_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            runs_scored = st.number_input(
                "Runs Scored", 
                min_value=0, 
                value=int(current['runs_scored']), 
                key="runs_update"
            )

        with col2:
            wickets_taken = st.number_input(
                "Wickets Taken", 
                min_value=0, 
                value=int(current['wickets_taken']), 
                key="wickets_update"
            )

        with col3:
            format_options = ["One Day", "Test", "T20"]
            current_format_index = format_options.index(current['format']) if current['format'] in format_options else 0
            format_type = st.selectbox(
                "Format", 
                options=format_options,
                index=current_format_index,
                key="format_update"
            )

        avg_val = st.number_input(
            "Average", 
            min_value=0.0, 
            value=float(current['avg']) if current['avg'] else 0.0, 
            key="avg_update"
        )

        submitted = st.form_submit_button("💾 Update Performance", use_container_width=True)

        if submitted:
            query = """UPDATE player_performance SET runs_scored = %s, wickets_taken = %s, format = %s, avg = %s
                       WHERE performance_id = %s"""
            params = (runs_scored, wickets_taken, format_type, avg_val, performance_id)
            if execute_query(query, params):
                st.success("✅ Player performance updated successfully!")
                st.balloons()
            else:
                st.error("❌ Failed to update performance")

    # Show statistics
    st.markdown("---")
    st.subheader("📈 Team Statistics")
    
    stats_query = """
    SELECT 
        t.team_name,
        COUNT(DISTINCT p.player_id) as total_players,
        SUM(pp.runs_scored) as total_runs,
        SUM(pp.wickets_taken) as total_wickets,
        AVG(pp.runs_scored) as avg_runs
    FROM player_performance pp
    JOIN player p ON pp.player_id = p.player_id
    JOIN team t ON p.team_id = t.team_id
    """
    
    if selected_team != "All Teams":
        stats_query += " WHERE t.team_name = %s"
        stats = execute_query(stats_query + " GROUP BY t.team_id, t.team_name", (selected_team,), fetch=True)
    else:
        stats = execute_query(stats_query + " GROUP BY t.team_id, t.team_name", fetch=True)
    
    if stats:
        stats_df = pd.DataFrame(stats)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

def create_award():
    st.subheader("Add New Award")
    with st.form(key="create_award_form"):
        award_name = st.text_input("Award Name")
        # Get player options from DB
        players = execute_query("SELECT player_id, CONCAT(f_name, ' ', l_name) AS name FROM player ORDER BY name", fetch=True)
        player_options = {f"{p['name']} (ID: {p['player_id']})": p['player_id'] for p in players} if players else {}

        player_id = st.selectbox("Select Player", options=list(player_options.keys()))
        player_id_val = player_options[player_id] if player_id else None

        # Get match options from DB
        matches = execute_query("SELECT match_id, date_of_match FROM matches ORDER BY date_of_match DESC", fetch=True)
        match_options = {f"Match {m['match_id']} on {m['date_of_match']}": m['match_id'] for m in matches} if matches else {}

        match_id = st.selectbox("Select Match", options=list(match_options.keys()))
        match_id_val = match_options[match_id] if match_id else None

        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Award")
        if submitted:
            insert_q = "INSERT INTO award (award_name, player_id, match_id, day, month, year, description) VALUES (%s, %s, %s, DAY(CURDATE()), MONTH(CURDATE()), YEAR(CURDATE()), %s)"
            params = (award_name, player_id_val, match_id_val, description)
            if execute_query(insert_q, params):
                st.success("Award added successfully!")
            else:
                st.error("Failed to add award.")

def read_awards():
    st.subheader("View All Awards")
    query = """
        SELECT 
            award_id,
            award_name,
            CONCAT(p.f_name, ' ', p.l_name) AS player_name,
            m.match_id,
            m.date_of_match,
            a.description
        FROM award a
        JOIN player p ON a.player_id = p.player_id
        JOIN matches m ON a.match_id = m.match_id
        ORDER BY m.date_of_match DESC;
    """
    awards = execute_query(query, fetch=True)
    if awards:
        df = pd.DataFrame(awards)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No awards found.")

def update_award():
    st.subheader("Update Award")
    awards = execute_query("SELECT award_id, award_name, description FROM award ORDER BY award_id", fetch=True)
    award_options = {f"{a['award_name']} (ID: {a['award_id']})": (a['award_id'], a['description']) for a in awards} if awards else {}
    selected = st.selectbox("Select Award to Update", options=list(award_options.keys()))
    award_id = award_options[selected][0] if selected else None
    current_desc = award_options[selected][1] if selected else ""
    new_award_name = st.text_input("New Award Name", value=selected.split(" (ID:")[0] if selected else "")
    new_desc = st.text_area("New Description", value=current_desc)
    if st.button("Update Award"):
        update_q = "UPDATE award SET award_name=%s, description=%s WHERE award_id=%s"
        params = (new_award_name, new_desc, award_id)
        if execute_query(update_q, params):
            st.success("Award updated successfully!")
        else:
            st.error("Failed to update award.")

def delete_award():
    st.subheader("Delete Award")
    awards = execute_query("SELECT award_id, award_name FROM award ORDER BY award_id", fetch=True)
    award_options = {f"{a['award_name']} (ID: {a['award_id']})": a['award_id'] for a in awards} if awards else {}
    selected = st.selectbox("Select Award to Delete", options=list(award_options.keys()))
    award_id = award_options[selected] if selected else None
    if st.button("Confirm Delete"):
        del_q = "DELETE FROM award WHERE award_id=%s"
        if execute_query(del_q, (award_id,)):
            st.success("Award deleted successfully!")
        else:
            st.error("Failed to delete award.")


# ADVANCED QUERIES
def nested_query():
    """Nested query - Players above average"""
    st.subheader("🔍 Nested Query: Players Above Average")

    query = """
    SELECT p.player_id, CONCAT(p.f_name, ' ', p.l_name) as player_name, 
           t.team_name, pp.runs_scored, pp.format
    FROM player p
    JOIN team t ON p.team_id = t.team_id
    JOIN player_performance pp ON p.player_id = pp.player_id
    WHERE pp.runs_scored > (
        SELECT AVG(runs_scored) FROM player_performance
    )
    ORDER BY pp.runs_scored DESC
    """

    results = execute_query(query, fetch=True)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        avg_result = execute_query("SELECT AVG(runs_scored) as avg_runs FROM player_performance", fetch=True)
        if avg_result and avg_result[0]['avg_runs']:
            st.info(f"Average runs scored: {float(avg_result[0]['avg_runs']):.2f}")
    else:
        st.warning("No results found")


def join_query():
    """Join query - Player performance"""
    st.subheader("🔗 Join Query: Player Performance Details")

    query = """
    SELECT 
        CONCAT(p.f_name, ' ', p.l_name) as player_name,
        t.team_name,
        r.role_name,
        pp.runs_scored,
        pp.wickets_taken,
        pp.format,
        m.date_of_match,
        m.location
    FROM player p
    INNER JOIN team t ON p.team_id = t.team_id
    INNER JOIN role r ON p.role_id = r.role_id
    INNER JOIN player_performance pp ON p.player_id = pp.player_id
    INNER JOIN matches m ON pp.match_id = m.match_id
    ORDER BY pp.runs_scored DESC, pp.wickets_taken DESC
    """

    results = execute_query(query, fetch=True)

    if results:
        df = pd.DataFrame(results)

        col1, col2 = st.columns(2)

        with col1:
            selected_team = st.multiselect("Filter by Team", 
                                          options=sorted(df['team_name'].unique()) if len(df) > 0 else [])
        with col2:
            selected_format = st.multiselect("Filter by Format", 
                                            options=sorted(df['format'].unique()) if len(df) > 0 else [])

        filtered_df = df.copy()
        if selected_team:
            filtered_df = filtered_df[filtered_df['team_name'].isin(selected_team)]
        if selected_format:
            filtered_df = filtered_df[filtered_df['format'].isin(selected_format)]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No results found")


def aggregate_query():
    """Aggregate query - Team statistics"""
    st.subheader("📊 Aggregate Query: Team Statistics")

    query = """
    SELECT 
        t.team_name,
        COUNT(DISTINCT p.player_id) as total_players,
        SUM(CASE WHEN m.winning_team_id = t.team_id THEN 1 ELSE 0 END) as matches_won,
        SUM(CASE WHEN m.losing_team_id = t.team_id THEN 1 ELSE 0 END) as matches_lost,
        COALESCE(SUM(pp.runs_scored), 0) as total_runs,
        COALESCE(SUM(pp.wickets_taken), 0) as total_wickets,
        COALESCE(AVG(pp.runs_scored), 0) as avg_runs_per_match
    FROM team t
    LEFT JOIN player p ON t.team_id = p.team_id
    LEFT JOIN player_performance pp ON p.player_id = pp.player_id
    LEFT JOIN matches m ON pp.match_id = m.match_id
    GROUP BY t.team_id, t.team_name
    ORDER BY matches_won DESC
    """

    results = execute_query(query, fetch=True)

    if results:
        df = pd.DataFrame(results)

        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Teams", len(df))
        with col2:
            st.metric("Total Players", int(df['total_players'].sum()))
        with col3:
            st.metric("Total Wins", int(df['matches_won'].sum()))
        with col4:
            st.metric("Total Runs", int(df['total_runs'].sum()))

        st.dataframe(df, use_container_width=True, hide_index=True)

        chart_data = df[['team_name', 'matches_won', 'matches_lost']].set_index('team_name')
        st.bar_chart(chart_data)
    else:
        st.warning("No results found")


# PROCEDURES & FUNCTIONS
def call_procedure():
    """Call stored procedure"""
    st.subheader("🔧 Stored Procedure: Get Players by Team")

    teams = execute_query("SELECT team_name FROM team ORDER BY team_name", fetch=True)
    team_list = [t['team_name'] for t in teams] if teams else []

    if not team_list:
        st.error("No teams available")
        return

    selected_team = st.selectbox("Select Team", options=team_list)

    if st.button("▶️ Execute Procedure", use_container_width=True):
        conn = init_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.callproc('GetPlayersByTeam', [selected_team])

                players = []
                for result in cursor.stored_results():
                    players = result.fetchall()

                cursor.close()

                if players:
                    df = pd.DataFrame(players)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No players found for this team")
            except Error as e:
                st.error(f"Error: {str(e)}")
            finally:
                if conn.is_connected():
                    conn.close()


def call_function():
    """Call function"""
    st.subheader("⚡ Function: Get Player Batting Average")

    players = execute_query(
        "SELECT player_id, CONCAT(f_name, ' ', l_name) as name FROM player ORDER BY f_name",
        fetch=True
    )

    if not players:
        st.info("No players available")
        return

    player_options = {f"{p['name']} (ID: {p['player_id']})" : p['player_id'] for p in players}
    selected = st.selectbox("Select Player", options=list(player_options.keys()))
    player_id = player_options[selected]

    if st.button("📊 Calculate Average", use_container_width=True):
        result = execute_query(
            "SELECT GetPlayerBattingAvg(%s) as batting_avg",
            (player_id,),
            fetch=True
        )

        if result and result[0]:
            avg = result[0]['batting_avg']
            if hasattr(avg, '__float__'):
                avg = float(avg)
            st.metric("Batting Average", f"{avg:.2f}")

            perfs = execute_query(
                "SELECT match_id, runs_scored, format FROM player_performance WHERE player_id = %s",
                (player_id,),
                fetch=True
            )

            if perfs:
                st.subheader("Performance History")
                df = pd.DataFrame(perfs)
                st.dataframe(df, use_container_width=True, hide_index=True)


# TRIGGERS DEMO
def triggers_demo():
    """Show trigger demonstrations"""
    st.subheader("⚡ Trigger Demonstrations")

    tab1, tab2 = st.tabs(["Trigger 1: Age Calculator", "Trigger 2: Role Promoter"])

    with tab1:
        st.subheader("Auto-calculate Age from DOB")
        st.markdown("""
        **When it fires:** BEFORE INSERT on player table

        **What it does:** Automatically calculates age from date of birth
        """)
        st.code("""
DELIMITER //
CREATE TRIGGER trg_set_age
BEFORE INSERT ON player
FOR EACH ROW
BEGIN
    SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.dob, CURDATE());
END;
//
DELIMITER ;
        """, language="sql")

    with tab2:
        st.subheader("Promote to All-Rounder")
        st.markdown("""
        **When it fires:** AFTER INSERT on player_performance table

        **Condition:** Runs >= 50 AND Wickets >= 3

        **Action:** Updates player role to All-Rounder
        """)
        st.code("""
DELIMITER //
CREATE TRIGGER trg_promote_to_allrounder
AFTER INSERT ON player_performance
FOR EACH ROW
BEGIN
  IF NEW.runs_scored >= 50 AND NEW.wickets_taken >= 3 THEN
    UPDATE player
    SET role_id = 3
    WHERE player_id = NEW.player_id;
  END IF;
END;
//
DELIMITER ;
        """, language="sql")

# CREATE NEW MATCH
def create_match():
    """Create new match and add player performances"""
    st.subheader("➕ Create New Match")
    
    with st.form(key="create_match_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            match_id = st.number_input("Match ID", min_value=1, step=1, key="new_match_id")
            
            teams = execute_query("SELECT team_id, team_name FROM team ORDER BY team_name", fetch=True)
            team_options = {t['team_name']: t['team_id'] for t in teams} if teams else {}
            
            if not team_options:
                st.error("No teams available")
                return
            
            winning_team = st.selectbox("Winning Team", list(team_options.keys()), key="new_win_team")
            losing_team = st.selectbox("Losing Team", list(team_options.keys()), key="new_lose_team")
        
        with col2:
            date_of_match = st.date_input("Match Date", key="new_match_date")
            location = st.text_input("Match Location", key="new_match_location")
            
            tournaments = execute_query("SELECT tournament_id, tournament_name FROM tournament ORDER BY tournament_name", fetch=True)
            tournament_options = {t['tournament_name']: t['tournament_id'] for t in tournaments} if tournaments else {}
            
            if not tournament_options:
                st.error("No tournaments available")
                return
            
            tournament = st.selectbox("Tournament", list(tournament_options.keys()), key="new_tournament")
        
        submitted = st.form_submit_button("✅ Create Match", use_container_width=True)
        
        if submitted:
            if winning_team == losing_team:
                st.error("Winning and Losing teams cannot be the same!")
            else:
                # Check if match already exists
                existing = execute_query(
                    "SELECT match_id FROM matches WHERE match_id = %s",
                    (match_id,),
                    fetch=True
                )
                
                if existing:
                    st.error(f"Match with ID {match_id} already exists")
                else:
                    query = """INSERT INTO matches (match_id, winning_team_id, losing_team_id, date_of_match, location, tournament_id)
                              VALUES (%s, %s, %s, %s, %s, %s)"""
                    params = (match_id, team_options[winning_team], team_options[losing_team], 
                             date_of_match, location, tournament_options[tournament])
                    
                    if execute_query(query, params):
                        st.success(f"Match {match_id} created successfully!")
                        st.session_state.created_match_id = match_id
                        st.rerun()
                    else:
                        st.error("Failed to create match")


# ADD PLAYER PERFORMANCE FOR MATCH
def add_player_performance_for_match():
    """Add player performances for a specific match with team filtering"""
    st.subheader("📊 Add Player Performance to Match")
    
    matches = execute_query(
        """SELECT m.match_id, CONCAT('Match ', m.match_id, ': ', t1.team_name, ' vs ', t2.team_name, ' on ', m.date_of_match) as name
           FROM matches m
           JOIN team t1 ON m.winning_team_id = t1.team_id
           JOIN team t2 ON m.losing_team_id = t2.team_id
           ORDER BY m.date_of_match DESC""", fetch=True)
    
    if not matches:
        st.info("No matches available. Create a match first!")
        return
    
    match_options = {m['name']: m['match_id'] for m in matches}
    selected_match = st.selectbox("Select Match", options=list(match_options.keys()))
    match_id = match_options[selected_match]
    
    match_data = execute_query(
        """SELECT m.*, t1.team_name as winning_team, t2.team_name as losing_team
           FROM matches m
           JOIN team t1 ON m.winning_team_id = t1.team_id
           JOIN team t2 ON m.losing_team_id = t2.team_id
           WHERE m.match_id = %s""", (match_id,), fetch=True)
    
    if not match_data:
        st.error("Match not found")
        return
    
    match_info = match_data[0]
    
    st.info(f"**Match Details:** Winner: {match_info['winning_team']} - Loser: {match_info['losing_team']} - Date: {match_info['date_of_match']} - Location: {match_info['location']}")
    
    # Filter players by the two teams playing
    teams_playing = [match_info['winning_team'], match_info['losing_team']]
    selected_team = st.selectbox("Filter players by Team", options=teams_playing)
    
    # Fetch players only from selected team
    players = execute_query(
        """SELECT player_id, CONCAT(f_name, ' ', l_name) as name
           FROM player p
           JOIN team t ON p.team_id = t.team_id
           WHERE t.team_name = %s
           ORDER BY name""", (selected_team,), fetch=True)
    
    if not players:
        st.info(f"No players found for team {selected_team}")
        return
    
    player_options = {p['name']: p['player_id'] for p in players}
    
    with st.form(key="add_performance_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_player = st.selectbox("Select Player", list(player_options.keys()))
            performance_id = st.number_input("Performance ID", min_value=1, step=1)
        with col2:
            runs = st.number_input("Runs Scored", min_value=0, step=1)
            wickets = st.number_input("Wickets Taken", min_value=0, step=1)
        with col3:
            format_type = st.selectbox("Format", options=["One Day", "Test", "T20"])
            avg = st.number_input("Average", min_value=0.0, step=0.1)
        
        submitted = st.form_submit_button("➕ Add Performance")
        
        if submitted:
            existing = execute_query(
                "SELECT performance_id FROM player_performance WHERE performance_id = %s",
                (performance_id,), fetch=True)
            
            if existing:
                st.error(f"Performance with ID {performance_id} already exists")
            else:
                query = """INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params = (performance_id, player_options[selected_player], match_id, runs, wickets, format_type, avg)
                
                if execute_query(query, params):
                    st.success("Performance record added successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to add performance record")
    
    # Show existing performances for this match
    st.markdown("---")
    st.subheader("Existing Performances in this Match")
    
    existing_perfs = execute_query(
        """SELECT pp.performance_id, p.f_name, p.l_name, pp.runs_scored, pp.wickets_taken, pp.format, pp.avg
           FROM player_performance pp
           JOIN player p ON pp.player_id = p.player_id
           WHERE pp.match_id = %s
           ORDER BY pp.performance_id""", (match_id,), fetch=True)
    
    if existing_perfs:
        df = pd.DataFrame(existing_perfs)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No performances added yet for this match")
def show_awards_and_recognition():
    st.subheader("Awards and Recognition")
    query = """
        SELECT 
            a.award_name,
            p.f_name AS first_name,
            p.l_name AS last_name,
            m.match_id,
            m.date_of_match,
            a.description
        FROM award a
        JOIN player p ON a.player_id = p.player_id
        JOIN matches m ON a.match_id = m.match_id
        ORDER BY m.date_of_match DESC;
    """
    awards = execute_query(query, fetch=True)
    if awards:
        df = pd.DataFrame(awards)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No awards or recognition found.")

# MAIN APPLICATION
def main_app():
    """Main application interface"""
    st.title("🏏 Cricket Database Manager")

    with st.sidebar:
        st.markdown("---")
        st.header("👤 User Profile")
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role.upper()}")

        if st.button("🚪 Logout", use_container_width=True):
            logout()

        st.markdown("---")

        menu = st.radio(
            "📍 Navigation",
            ["📊 Dashboard", "📝 CRUD Operations", "🎯 Match Management", "⚙️ Updates", "🔍 Advanced Queries", 
             "🔧 Procedures & Functions", "⚡ Triggers Demo", "Awards CRUD","Awards and Recognition","ℹ️ About",]
        )

    # Main content
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            player_count = execute_query("SELECT COUNT(*) as count FROM player", fetch=True)
            count = player_count[0]['count'] if player_count else 0
            st.metric("Players", count)

        with col2:
            team_count = execute_query("SELECT COUNT(*) as count FROM team", fetch=True)
            count = team_count[0]['count'] if team_count else 0
            st.metric("Teams", count)

        with col3:
            match_count = execute_query("SELECT COUNT(*) as count FROM matches", fetch=True)
            count = match_count[0]['count'] if match_count else 0
            st.metric("Matches", count)

        with col4:
            tourn_count = execute_query("SELECT COUNT(*) as count FROM tournament", fetch=True)
            count = tourn_count[0]['count'] if tourn_count else 0
            st.metric("Tournaments", count)

        st.markdown("---")

        st.subheader("📋 Recent Matches")
        recent = execute_query("""
            SELECT m.match_id, t1.team_name as winner, t2.team_name as loser,
                   m.date_of_match, m.location, tour.tournament_name
            FROM matches m
            JOIN team t1 ON m.winning_team_id = t1.team_id
            JOIN team t2 ON m.losing_team_id = t2.team_id
            JOIN tournament tour ON m.tournament_id = tour.tournament_id
            ORDER BY m.date_of_match DESC
            LIMIT 5
        """, fetch=True)

        if recent:
            df = pd.DataFrame(recent)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No matches found")

    elif menu == "📝 CRUD Operations":
        st.header("📝 CRUD Operations")

        crud_tab = st.tabs(["✅ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"])

        with crud_tab[0]:
            if st.session_state.role == "admin":
                create_player()
            else:
                st.warning("⛔ Admin privileges required")

        with crud_tab[1]:
            read_players()

        with crud_tab[2]:
            if st.session_state.role == "admin":
                update_player()
            else:
                st.warning("⛔ Admin privileges required")

        with crud_tab[3]:
            if st.session_state.role == "admin":
                delete_player()
            else:
                st.warning("⛔ Admin privileges required")

    elif menu == "🎯 Match Management":
        st.header("🎯 Match Management")

        match_tab = st.tabs(["➕ Create Match", "📊 Add Player Performance"])

        with match_tab[0]:
            if st.session_state.role == "admin":
                create_match()
            else:
                st.warning("⛔ Admin privileges required")

        with match_tab[1]:
            if st.session_state.role == "admin":
                add_player_performance_for_match()
            else:
                st.warning("⛔ Admin privileges required")

    elif menu == "⚙️ Updates":
        st.header("⚙️ Updates")

        update_tab = st.tabs(["🔄 Update Match Details", "🔄 Update Player Performance & Scores"])

        with update_tab[0]:
            if st.session_state.role == "admin":
                update_match()
            else:
                st.warning("⛔ Admin privileges required")

        with update_tab[1]:
            if st.session_state.role == "admin":
                update_player_performance()
            else:
                st.warning("⛔ Admin privileges required")

    elif menu == "🔍 Advanced Queries":
        st.header("🔍 Advanced Queries")

        query_tab = st.tabs(["🎯 Nested Query", "🔗 Join Query", "📊 Aggregate Query"])

        with query_tab[0]:
            nested_query()

        with query_tab[1]:
            join_query()

        with query_tab[2]:
            aggregate_query()

    elif menu == "🔧 Procedures & Functions":
        st.header("🔧 Procedures & Functions")

        pf_tab = st.tabs(["📋 Stored Procedure", "⚙️ Function"])

        with pf_tab[0]:
            call_procedure()

        with pf_tab[1]:
            call_function()

    elif menu == "⚡ Triggers Demo":
        triggers_demo()
    elif menu == "Awards CRUD":
        st.header("Awards CRUD")
        crudtab = st.tabs(["Create", "Read", "Update", "Delete"])
        # Only admin sees all tabs; others see read only
        if st.session_state["role"] == "admin":
            with crudtab[0]: create_award()
            with crudtab[1]: read_awards()
            with crudtab[2]: update_award()
            with crudtab[3]: delete_award()
        else:
            with crudtab[1]: read_awards()
            for i in [0,2,3]:
                with crudtab[i]: st.warning("Admin privileges required.")

    elif menu == "Awards and Recognition":
        show_awards_and_recognition()

    elif menu == "ℹ️ About":
        st.header("ℹ️ About")
        st.markdown("""
        ### Cricket Database Management System

        **Version:** 3.2 - Match Management & Player Performance Updates

        **Features:**
        - ✅ User Authentication
        - ✅ CRUD Operations
        - ✅ Create New Matches
        - ✅ Add Player Performance to Matches
        - ✅ Update Match Details
        - ✅ Update Player Scores
        - ✅ Advanced Queries
        - ✅ Procedures & Functions
        - ✅ Triggers

        **Technology Stack:**
        - Python
        - Streamlit
        - MySQL
        - Pandas

        **Demo Users:**
        - Admin: admin / admin123
        - User: user / user123
        """)


# ENTRY POINT
if __name__ == "__main__":
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()
