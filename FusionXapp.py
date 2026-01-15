# FusionXapp.py
import streamlit as st

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="FusionX", layout="wide")
st.title("FusionX - Fusion Global Competition Platform")
st.markdown("💡 *Community-driven competitions for every Fusion student!*")

# -----------------------------
# Initialize Persistent State
# -----------------------------
if 'competitions' not in st.session_state:
    st.session_state.competitions = []  # list of competitions
if 'participants' not in st.session_state:
    st.session_state.participants = {}  # track participants per competition
if 'my_competitions' not in st.session_state:
    st.session_state.my_competitions = set()  # competitions created by this user
if 'joined_competitions' not in st.session_state:
    st.session_state.joined_competitions = set()  # prevent joining twice

# -----------------------------
# Sidebar Navigation
# -----------------------------
page = st.sidebar.radio("Navigation", ["Home", "Propose Competition", "Pending Competitions", "Portfolios"])


# -----------------------------
# Home Page: Active Competitions
# -----------------------------
if page == "Home":
    st.subheader("Active Competitions")
    active = [
        c for c in st.session_state.competitions 
        if len(st.session_state.participants.get(c['title'], [])) >= c['threshold']
    ]
    
    if not active:
        st.info("No active competitions yet.")
    for comp in active:
        participants = st.session_state.participants.get(comp['title'], [])
        st.markdown(f"### {comp['title']}")
        st.markdown(f"**Description:** {comp['description']}")
        st.markdown(f"**Participants Joined:** {len(participants)}/{comp['threshold']} ✅ ACTIVE")
        st.markdown("---")

# -----------------------------
# Competition Proposal Page
# -----------------------------
elif page == "Propose Competition":
    st.subheader("Propose a New Competition")
    with st.form("proposal_form"):
        title = st.text_input("Competition Title")
        description = st.text_area("Competition Description")
        threshold = st.number_input(
            "Joining Threshold (number of participants required to activate)", 
            min_value=1, value=15, step=1
        )
        submitted = st.form_submit_button("Submit Competition")
        
        if submitted:
            if title and description:
                if any(c['title'].lower() == title.lower() for c in st.session_state.competitions):
                    st.error("A competition with this title already exists!")
                else:
                    st.session_state.competitions.append({
                        "title": title,
                        "description": description,
                        "threshold": threshold
                    })
                    st.session_state.participants[title] = []  # initialize participants list
                    st.session_state.my_competitions.add(title)
                    st.success(f"Competition '{title}' submitted successfully!")
            else:
                st.error("Please provide both title and description.")

# -----------------------------
# Pending Competitions Page
# -----------------------------
elif page == "Pending Competitions":
    st.subheader("Pending Competitions (Join to Activate)")
    pending = [
        c for c in st.session_state.competitions 
        if len(st.session_state.participants.get(c['title'], [])) < c['threshold']
    ]
    
    if not pending:
        st.info("No pending competitions right now. Be the first to propose one!")
    
    for comp in pending:
        participants = st.session_state.participants.get(comp['title'], [])
        st.markdown(f"### {comp['title']}")
        st.markdown(f"**Description:** {comp['description']}")
        st.markdown(f"**Participants Joined:** {len(participants)}/{comp['threshold']} ⏳ PENDING")

        # Join button
        key_join = f"join_{comp['title']}"
        if st.button("Join Competition", key=key_join):
            if comp['title'] not in st.session_state.joined_competitions:
                st.session_state.participants[comp['title']].append("You")  # placeholder for user
                st.session_state.joined_competitions.add(comp['title'])
                st.success(f"You joined '{comp['title']}'!")
            else:
                st.warning("You have already joined this competition.")

        # Delete button (only if you created this competition)
        if comp['title'] in st.session_state.my_competitions:
            key_delete = f"delete_{comp['title']}"
            if st.button(f"Delete Competition '{comp['title']}'", key=key_delete):
                st.session_state.competitions = [
                    c for c in st.session_state.competitions if c['title'] != comp['title']
                ]
                st.session_state.participants.pop(comp['title'], None)
                st.session_state.my_competitions.remove(comp['title'])
                st.success(f"Competition '{comp['title']}' deleted.")
                st.experimental_set_query_params(refresh="true")
                st.stop()

        st.markdown("---")
# -----------------------------
# Portfolio Submission & Upload Page
# -----------------------------
if page == "Portfolios":
    st.subheader("Student Portfolio Builder & Submission")
    st.markdown(
        "Build your portfolio by adding multiple projects. "
        "Each project can have a field and optional file upload."
    )

    # Initialize session state
    if 'portfolios' not in st.session_state:
        st.session_state.portfolios = {}  # {student_name: [projects]}
    if 'current_projects' not in st.session_state:
        st.session_state.current_projects = []  # temporary projects before submission

    # Step 1: Enter student name
    student_name = st.text_input("Your Name")

    st.markdown("### Add a Project")
    with st.form("project_form"):
        project_title = st.text_input("Project Title")
        project_description = st.text_area("Project Description")
        field = st.selectbox("Field", ["AI", "Robotics", "Design", "Science", "Math", "Art", "Other"])
        upload_file = st.file_uploader("Upload File (optional)", type=["png","jpg","pdf","zip"])
        add_project = st.form_submit_button("Add Project")
        
        if add_project:
            if project_title and project_description and field:
                # Store project as dictionary
                st.session_state.current_projects.append({
                    "title": project_title,
                    "description": project_description,
                    "field": field,
                    "file": upload_file.name if upload_file else None,
                    "file_data": upload_file.read() if upload_file else None
                })
                st.success(f"Project '{project_title}' added to your portfolio!")
            else:
                st.error("Please fill out all fields to add a project.")

    # Step 2: Show current projects before submitting portfolio
    if st.session_state.current_projects:
        st.markdown("### Current Projects in This Portfolio")
        for i, p in enumerate(st.session_state.current_projects, start=1):
            st.markdown(f"{i}. **{p['title']}** ({p['field']})")
            st.markdown(f"{p['description']}")
            if p["file"]:
                st.markdown(f"**Uploaded File:** {p['file']}")
            st.markdown("---")

        # Step 3: Submit full portfolio
        if st.button("Submit Full Portfolio"):
            if student_name:
                if student_name not in st.session_state.portfolios:
                    st.session_state.portfolios[student_name] = []
                st.session_state.portfolios[student_name].extend(st.session_state.current_projects)
                st.session_state.current_projects = []  # clear temp projects
                st.success(f"Portfolio for '{student_name}' submitted successfully!")
            else:
                st.error("Please enter your name before submitting your portfolio.")

    # Step 4: Display all submitted portfolios
    if st.session_state.portfolios:
        st.markdown("## All Submitted Portfolios")
        for student, projects in st.session_state.portfolios.items():
            st.markdown(f"### {student}'s Portfolio")
            for i, p in enumerate(projects, start=1):
                st.markdown(f"{i}. **{p['title']}** ({p['field']})")
                st.markdown(f"{p['description']}")
                if p["file"]:
                    st.markdown(f"**Uploaded File:** {p['file']}")
                st.markdown("---")
    else:
        st.info("No portfolios submitted yet.")
# -----------------------------
# Voting Sidebar for Portfolios (append at the end)
# -----------------------------
import datetime

VOTE_LIMIT = 5      # votes per month
VOTE_RESET_DAYS = 30

# Initialize voting session state
if 'portfolio_votes' not in st.session_state:
    st.session_state.portfolio_votes = {}  # {student_name: {"yes": int, "no": int}}
if 'user_votes' not in st.session_state:
    st.session_state.user_votes = {}  # {voter_name: {"votes_left": int, "last_reset": date}}

st.sidebar.subheader("Vote on Student Portfolios")
voter_name = st.sidebar.text_input("Your Name (to vote)")

if voter_name:
    today = datetime.date.today()

    # Initialize voter info if first time
    if voter_name not in st.session_state.user_votes:
        st.session_state.user_votes[voter_name] = {"votes_left": VOTE_LIMIT, "last_reset": today}

    # Reset votes every 30 days
    last_reset = st.session_state.user_votes[voter_name]["last_reset"]
    if (today - last_reset).days >= VOTE_RESET_DAYS:
        st.session_state.user_votes[voter_name]["votes_left"] = VOTE_LIMIT
        st.session_state.user_votes[voter_name]["last_reset"] = today

    st.sidebar.markdown(f"Votes remaining this month: {st.session_state.user_votes[voter_name]['votes_left']}")

    # Show portfolios to vote on
    if 'portfolios' in st.session_state and st.session_state.portfolios:
        for student, projects in st.session_state.portfolios.items():
            if student == voter_name:
                continue  # skip voting on own portfolio

            votes = st.session_state.portfolio_votes.get(student, {"yes": 0, "no": 0})
            st.sidebar.markdown(f"**{student}'s Portfolio** ✅ {votes['yes']} | ❌ {votes['no']}")

            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button(f"YES {student}", key=f"yes_{voter_name}_{student}"):
                    if st.session_state.user_votes[voter_name]["votes_left"] > 0:
                        if student not in st.session_state.portfolio_votes:
                            st.session_state.portfolio_votes[student] = {"yes": 0, "no": 0}
                        st.session_state.portfolio_votes[student]["yes"] += 1
                        st.session_state.user_votes[voter_name]["votes_left"] -= 1
                        st.success(f"You voted YES for {student}'s portfolio!")
                    else:
                        st.warning("No votes left this month!")

            with col2:
                if st.button(f"NO {student}", key=f"no_{voter_name}_{student}"):
                    if st.session_state.user_votes[voter_name]["votes_left"] > 0:
                        if student not in st.session_state.portfolio_votes:
                            st.session_state.portfolio_votes[student] = {"yes": 0, "no": 0}
                        st.session_state.portfolio_votes[student]["no"] += 1
                        st.session_state.user_votes[voter_name]["votes_left"] -= 1
                        st.success(f"You voted NO for {student}'s portfolio!")
                    else:
                        st.warning("No votes left this month!")
# -----------------------------
# Special Recognition (Top 3 Portfolios)
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🌟 Special Recognition: Top 3 Portfolios")

# Build a list of (student, yes_votes) from portfolio_votes
ranking = []
for student, counts in st.session_state.portfolio_votes.items():
    yes_votes = counts.get("yes", 0)
    ranking.append((student, yes_votes))

# Sort the list by yes_votes descending
ranking.sort(key=lambda x: x[1], reverse=True)

# Get top 3 (or fewer if less than 3 portfolios exist)
top_3 = ranking[:3]

if top_3:
    for i, (student, yes_votes) in enumerate(top_3, start=1):
        st.sidebar.markdown(f"**{i}. {student}** — {yes_votes} votes")
else:
    st.sidebar.markdown("No portfolios have votes yet.")
# -----------------------------
# Submit Work for Current Active Competitions
# -----------------------------
st.markdown("---")
st.subheader("Submit Work for Active Competitions")
st.markdown(
    "Below are competitions that are currently active. "
    "Select a competition, enter your project details, and submit your work."
)

# Ensure competitions and participants exist
if 'competitions' not in st.session_state:
    st.session_state.competitions = []
if 'participants' not in st.session_state:
    st.session_state.participants = {}
if 'competition_submissions' not in st.session_state:
    st.session_state.competition_submissions = {}  # {competition_title: [submissions]}

# Filter active competitions: threshold reached
active_competitions = [
    c for c in st.session_state.competitions
    if len(st.session_state.participants.get(c['title'], [])) >= c['threshold']
]

if active_competitions:
    # Show competitions clearly
    st.markdown("### Current Active Competitions")
    for c in active_competitions:
        st.markdown(f"**{c['title']}**")
        st.markdown(f"Description: {c['description']}")
        st.markdown(f"Participants Joined: {len(st.session_state.participants.get(c['title'], []))}/{c['threshold']}")
        st.markdown("---")

    # Let student select which competition to submit to
    comp_titles = [c['title'] for c in active_competitions]
    selected_comp = st.radio("Select a competition to submit work to:", comp_titles)

    # Submission form
    with st.form("competition_submission_form"):
        submitter_name = st.text_input("Your Name")
        submission_title = st.text_input("Project/Work Title")
        submission_description = st.text_area("Description of Your Work")
        submission_file = st.file_uploader("Upload File (optional)", type=["png", "jpg", "pdf", "zip"])
        submit_work = st.form_submit_button("Submit Work")

        if submit_work:
            if submitter_name and submission_title and submission_description:
                submission = {
                    "submitter": submitter_name,
                    "title": submission_title,
                    "description": submission_description,
                    "file": submission_file.name if submission_file else None,
                    "file_data": submission_file.read() if submission_file else None
                }
                if selected_comp not in st.session_state.competition_submissions:
                    st.session_state.competition_submissions[selected_comp] = []
                st.session_state.competition_submissions[selected_comp].append(submission)
                st.success(f"Work '{submission_title}' submitted for '{selected_comp}'!")
            else:
                st.error("Please fill out all required fields before submitting.")

else:
    st.info("No active competitions available for submission at the moment.")

# Display all submissions
st.markdown("### Submitted Work for Competitions")
for comp_title, submissions in st.session_state.competition_submissions.items():
    st.markdown(f"#### {comp_title}")
    for i, s in enumerate(submissions, start=1):
        st.markdown(f"{i}. **{s['title']}** by {s['submitter']}")
        st.markdown(f"{s['description']}")
        if s["file"]:
            st.markdown(f"**Uploaded File:** {s['file']}")
        st.markdown("---")
# -----------------------------
# Enhanced Competition Submission Management
# -----------------------------
import datetime

st.markdown("---")
st.subheader("Manage Your Submissions")

# Ensure submissions exist
if 'competition_submissions' not in st.session_state:
    st.session_state.competition_submissions = {}  # {competition_title: [submissions]}

# Let student select their name
user_name = st.text_input("Enter your name to manage your submissions")

if user_name:
    user_submissions_exist = False
    for comp_title, submissions in st.session_state.competition_submissions.items():
        # Filter only submissions by this user
        user_subs = [s for s in submissions if s['submitter'] == user_name]
        if user_subs:
            user_submissions_exist = True
            st.markdown(f"### Your submissions for {comp_title}")

            # Sort submissions by date if stored, otherwise by title
            # We'll store submission time if not already stored
            for s in user_subs:
                if 'timestamp' not in s:
                    s['timestamp'] = datetime.datetime.now()

            sort_option = st.radio(f"Sort your submissions for {comp_title} by:", ["Date", "Title"], key=comp_title)
            if sort_option == "Date":
                user_subs.sort(key=lambda x: x['timestamp'], reverse=True)
            else:
                user_subs.sort(key=lambda x: x['title'])

            # Display submissions with Update/Delete buttons
            for i, s in enumerate(user_subs, start=1):
                st.markdown(f"{i}. **{s['title']}** ({s['timestamp'].strftime('%Y-%m-%d %H:%M')})")
                st.markdown(f"{s['description']}")
                if s['file']:
                    st.markdown(f"**Uploaded File:** {s['file']}")

                col1, col2, col3 = st.columns(3)

                # Update submission
                with col1:
                    if st.button(f"Update {s['title']}", key=f"update_{comp_title}_{i}"):
                        # Allow updating title, description, and file
                        new_title = st.text_input("New Title", value=s['title'], key=f"new_title_{comp_title}_{i}")
                        new_desc = st.text_area("New Description", value=s['description'], key=f"new_desc_{comp_title}_{i}")
                        new_file = st.file_uploader("Replace File (optional)", type=["png","jpg","pdf","zip"], key=f"new_file_{comp_title}_{i}")
                        if st.button("Confirm Update", key=f"confirm_update_{comp_title}_{i}"):
                            s['title'] = new_title
                            s['description'] = new_desc
                            if new_file:
                                s['file'] = new_file.name
                                s['file_data'] = new_file.read()
                            st.success(f"Submission '{s['title']}' updated successfully!")

                # Delete submission
                with col2:
                    if st.button(f"Delete {s['title']}", key=f"delete_{comp_title}_{i}"):
                        st.session_state.competition_submissions[comp_title].remove(s)
                        st.success(f"Submission '{s['title']}' deleted!")

                st.markdown("---")

    if not user_submissions_exist:
        st.info("You have no submissions yet.")

# -----------------------------
# Notify on New Submissions
# -----------------------------
if 'last_submission_count' not in st.session_state:
    st.session_state.last_submission_count = sum(len(s) for s in st.session_state.competition_submissions.values())

current_count = sum(len(s) for s in st.session_state.competition_submissions.values())
if current_count > st.session_state.last_submission_count:
    st.toast("🎉 New submission added to a competition!")
    st.session_state.last_submission_count = current_count
# -----------------------------
# Field-Based Competition Filtering
# -----------------------------
st.markdown("---")
st.subheader("Find Competitions by Field")
st.markdown("Select your field of interest to see competitions tailored for you.")

# Ensure competitions exist
if 'competitions' not in st.session_state:
    st.session_state.competitions = []

# Define possible fields
fields = ["All", "AI", "Robotics", "Design", "Science", "Math", "Business", "Art", "Other"]

# Let student select a field
chosen_field = st.selectbox("Select your field", fields)

# Filter competitions by field
if chosen_field == "All":
    filtered_comps = st.session_state.competitions
else:
    filtered_comps = [c for c in st.session_state.competitions if c.get("field") == chosen_field]

if filtered_comps:
    st.markdown(f"### Competitions in {chosen_field}")
    for c in filtered_comps:
        st.markdown(f"**{c['title']}**")
        st.markdown(f"Description: {c['description']}")
        threshold = c.get('threshold', 'N/A')
        participants = len(st.session_state.participants.get(c['title'], [])) if 'participants' in st.session_state else 0
        st.markdown(f"Participants Joined: {participants}/{threshold}")
        st.markdown("---")
else:
    st.info(f"No competitions found for the field '{chosen_field}'.")
# -----------------------------
# Add-On: Propose Competition with Field
# -----------------------------
st.markdown("---")
st.subheader("Propose a New Competition")

# Initialize competitions list if it doesn't exist
if 'competitions' not in st.session_state:
    st.session_state.competitions = []

# Initialize participants dictionary if needed
if 'participants' not in st.session_state:
    st.session_state.participants = {}

with st.form("propose_competition_form_with_field"):
    title = st.text_input("Competition Title")
    description = st.text_area("Description")
    threshold = st.number_input("Threshold (number of students required)", min_value=1, value=5)
    
    # Field dropdown
    field = st.selectbox("Field of Competition", ["AI", "Robotics", "Design", "Science", "Math", "Business", "Art", "Other"])
    
    propose = st.form_submit_button("Propose Competition")
    
    if propose:
        if title and description:
            # Create competition dictionary with field
            new_comp = {
                "title": title,
                "description": description,
                "threshold": threshold,
                "field": field
            }
            st.session_state.competitions.append(new_comp)
            st.success(f"Competition '{title}' proposed in the '{field}' field!")
        else:
            st.error("Please fill out all required fields.")
# -----------------------------
# Add-On: Student Accounts for Recognized Submissions
# -----------------------------
st.markdown("---")
st.subheader("Student Account Creation")

# Initialize account storage
if 'student_accounts' not in st.session_state:
    st.session_state.student_accounts = {}  # {email: {"name": name}}

# --- Account Creation Form ---
with st.form("create_account_form"):
    student_name = st.text_input("Your Name", key="account_name")
    student_email = st.text_input("Your Email", key="account_email")
    create_account = st.form_submit_button("Create Account")
    
    if create_account:
        if student_name and student_email:
            if student_email not in st.session_state.student_accounts:
                st.session_state.student_accounts[student_email] = {"name": student_name}
                st.success(f"Account created for {student_name} ({student_email})!")
            else:
                st.warning("An account with this email already exists.")
        else:
            st.error("Please fill out both name and email.")

# --- Submission Form Using Account ---
st.markdown("### Submit Work Using Your Account")

if st.session_state.student_accounts:
    # Select account
    student_email_select = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()))
    student_name = st.session_state.student_accounts[student_email_select]["name"]

    # Show submission form
    with st.form("submission_with_account"):
        submission_title = st.text_input("Project/Work Title", key="account_submission_title")
        submission_description = st.text_area("Description of Your Work", key="account_submission_desc")
        submission_file = st.file_uploader("Upload File (optional)", type=["png","jpg","pdf","zip"], key="account_submission_file")
        selected_comp = st.selectbox(
            "Select Competition to Submit To",
            [c['title'] for c in st.session_state.competitions] if 'competitions' in st.session_state else []
        )
        submit_work_account = st.form_submit_button("Submit Work")

        if submit_work_account:
            if submission_title and submission_description and selected_comp:
                submission = {
                    "submitter_name": student_name,
                    "submitter_email": student_email_select,
                    "title": submission_title,
                    "description": submission_description,
                    "file": submission_file.name if submission_file else None,
                    "file_data": submission_file.read() if submission_file else None,
                    "timestamp": datetime.datetime.now()
                }

                # Store submission in competition_submissions
                if 'competition_submissions' not in st.session_state:
                    st.session_state.competition_submissions = {}
                if selected_comp not in st.session_state.competition_submissions:
                    st.session_state.competition_submissions[selected_comp] = []

                st.session_state.competition_submissions[selected_comp].append(submission)
                st.success(f"Work '{submission_title}' submitted for '{selected_comp}' as {student_name}!")
            else:
                st.error("Please fill out all required fields before submitting.")

    # Show all submissions with student name/email
    st.markdown("### All Submissions with Account Info")
    if 'competition_submissions' in st.session_state and st.session_state.competition_submissions:
        for comp_title, submissions in st.session_state.competition_submissions.items():
            st.markdown(f"#### {comp_title}")
            for i, s in enumerate(submissions, start=1):
                st.markdown(f"{i}. **{s['title']}** by {s['submitter_name']} ({s['submitter_email']})")
                st.markdown(f"{s['description']}")
                if s['file']:
                    st.markdown(f"**Uploaded File:** {s['file']}")
                st.markdown("---")
# -----------------------------
# Add-On: Field-Based Chat Rooms
# -----------------------------
st.markdown("---")
st.subheader("Field-Based Chat Rooms")
st.markdown("Join a chat room for your field and team up with other students!")

# Initialize chat room storage
if 'chat_rooms' not in st.session_state:
    st.session_state.chat_rooms = {}  # {field_name: [{"user": user_name, "message": msg, "timestamp": datetime}]}

# Let student select their name (or account if using previous add-on)
if 'student_accounts' in st.session_state and st.session_state.student_accounts:
    chat_user_email = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()), key="chat_user_email")
    chat_user_name = st.session_state.student_accounts[chat_user_email]["name"]
else:
    chat_user_name = st.text_input("Enter your name to join chat")

# Field selection for chat
fields = ["AI", "Robotics", "Design", "Science", "Math", "Business", "Art", "Other"]
selected_field = st.selectbox("Select a chat room (by field)", fields, key="chat_field_select")

# Initialize chat room if empty
if selected_field not in st.session_state.chat_rooms:
    st.session_state.chat_rooms[selected_field] = []

# Display chat messages
st.markdown(f"### Chat Room: {selected_field}")
if st.session_state.chat_rooms[selected_field]:
    for msg in st.session_state.chat_rooms[selected_field]:
        timestamp = msg['timestamp'].strftime("%Y-%m-%d %H:%M")
        st.markdown(f"**{msg['user']}** ({timestamp}): {msg['message']}")
else:
    st.info("No messages yet. Start the conversation!")

# Input for new message
new_message = st.text_input("Type your message here", key="new_chat_msg")
if st.button("Send Message"):
    if new_message and chat_user_name:
        st.session_state.chat_rooms[selected_field].append({
            "user": chat_user_name,
            "message": new_message,
            "timestamp": datetime.datetime.now()
        })
        st.experimental_rerun()  # refresh chat to show the new message
    else:
        st.warning("Please enter your name and a message to send.")
# -----------------------------
# Add-On: User Accounts & Profile Pages
# -----------------------------
st.markdown("---")
st.subheader("User Accounts & Profile Pages")
st.markdown("Create an account to track your portfolios, competitions, votes, and achievements.")

import base64

# Initialize accounts if not present
if 'student_accounts' not in st.session_state:
    st.session_state.student_accounts = {}  # {email: {"name": name, "field": [], "avatar": file, "votes": 0, "badges": []}}

# --- Account Creation / Update ---
with st.form("account_creation_form"):
    account_name = st.text_input("Your Name", key="profile_name")
    account_email = st.text_input("Your Email", key="profile_email")
    account_field = st.multiselect("Your Field Interests", ["AI","Robotics","Design","Science","Math","Business","Art","Other"])
    account_avatar = st.file_uploader("Upload Profile Picture (optional)", type=["png","jpg","jpeg"], key="profile_avatar")
    create_account = st.form_submit_button("Create / Update Account")
    
    if create_account:
        if account_name and account_email:
            avatar_data = account_avatar.read() if account_avatar else None
            if account_email not in st.session_state.student_accounts:
                st.session_state.student_accounts[account_email] = {
                    "name": account_name,
                    "field": account_field,
                    "avatar": avatar_data,
                    "votes": 0,
                    "badges": []
                }
                st.success(f"Account created for {account_name}!")
            else:
                # Update existing account
                st.session_state.student_accounts[account_email]["name"] = account_name
                st.session_state.student_accounts[account_email]["field"] = account_field
                if avatar_data:
                    st.session_state.student_accounts[account_email]["avatar"] = avatar_data
                st.success(f"Account updated for {account_name}!")
        else:
            st.error("Please fill in at least your name and email.")

# --- Profile Page Viewer ---
st.markdown("### View Your Profile")
if st.session_state.student_accounts:
    selected_email = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()), key="profile_select")
    account = st.session_state.student_accounts[selected_email]
    
    # Display avatar
    if account.get("avatar"):
        avatar_b64 = base64.b64encode(account["avatar"]).decode("utf-8")
        st.markdown(f'<img src="data:image/png;base64,{avatar_b64}" width="100" style="border-radius:50%">', unsafe_allow_html=True)
    
    st.markdown(f"**Name:** {account['name']}")
    st.markdown(f"**Email:** {selected_email}")
    st.markdown(f"**Fields of Interest:** {', '.join(account['field']) if account['field'] else 'None'}")
    st.markdown(f"**Votes Received:** {account.get('votes', 0)}")
    
    # Show badges
    if account.get("badges"):
        st.markdown("**Achievements / Badges:**")
        st.markdown(", ".join(account["badges"]))
    else:
        st.markdown("**Achievements / Badges:** None yet")
    
    # Show portfolio projects
    if 'portfolios' in st.session_state and selected_email in st.session_state.portfolios:
        st.markdown("**Portfolio Projects:**")
        for proj in st.session_state.portfolios[selected_email]:
            st.markdown(f"- {proj['title']} ({proj.get('field','No field')})")
    else:
        st.markdown("**Portfolio Projects:** None yet")
    
    # Show competitions joined
    if 'participants' in st.session_state:
        joined_comps = [comp for comp, users in st.session_state.participants.items() if account['name'] in users]
        st.markdown(f"**Competitions Joined:** {', '.join(joined_comps) if joined_comps else 'None'}")
    else:
        st.markdown("**Competitions Joined:** None yet")
# -----------------------------
# Add-On: Automatic Badges & Vote Tracking
# -----------------------------
st.markdown("---")
st.subheader("Automatic Badges & Vote Tracking")

# Initialize badges if not present
if 'student_accounts' not in st.session_state:
    st.session_state.student_accounts = {}  # Ensure accounts exist

if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {}  # {email: [project_dicts]}

if 'portfolio_votes' not in st.session_state:
    st.session_state.portfolio_votes = {}  # {email: total_votes}

# --- Grant Badge for First Portfolio Submission ---
for email, projects in st.session_state.portfolios.items():
    if projects:
        account = st.session_state.student_accounts.get(email)
        if account:
            if "First Portfolio Submitted" not in account['badges']:
                account['badges'].append("🏆 First Portfolio Submitted")
                st.toast(f"{account['name']} earned the badge: First Portfolio Submitted!")

# --- Grant Badge for Multiple Fields Participation ---
for email, account in st.session_state.student_accounts.items():
    if len(account.get('field', [])) >= 2:
        if "Multi-Field Participant" not in account['badges']:
            account['badges'].append("🌟 Multi-Field Participant")
            st.toast(f"{account['name']} earned the badge: Multi-Field Participant!")

# --- Grant Badges for Top 3 in Competitions ---
if 'competition_votes' in st.session_state:
    # competition_votes = {competition_title: [{"email": email, "votes": x}, ...]}
    for comp_title, votes_list in st.session_state.competition_votes.items():
        # Sort descending
        sorted_votes = sorted(votes_list, key=lambda x: x['votes'], reverse=True)
        for i, top in enumerate(sorted_votes[:3]):  # Top 3
            email = top['email']
            account = st.session_state.student_accounts.get(email)
            if account:
                badge_name = f"🏅 Top {i+1} in {comp_title}"
                if badge_name not in account['badges']:
                    account['badges'].append(badge_name)
                    st.toast(f"{account['name']} earned the badge: {badge_name}!")

# --- Increment Votes in Account Whenever Portfolio Gets Voted ---
# portfolio_votes = {email: total_votes}
for email, vote_count in st.session_state.portfolio_votes.items():
    account = st.session_state.student_accounts.get(email)
    if account:
        account['votes'] = vote_count
# -----------------------------
# Add-On: Special Features Tab
# -----------------------------
import io
from fpdf import FPDF

st.markdown("---")
st.subheader("Special Features")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "AI Suggestions",
    "Mentor Feedback",
    "Portfolio Export",
    "Integration",
    "Gamified Challenges"
])

# =======================
# Tab 1: AI Suggestions
# =======================
with tab1:
    st.markdown("### AI Recommendations for You")
    if 'student_accounts' in st.session_state and st.session_state.student_accounts:
        student_email = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()), key="ai_suggestions")
        student = st.session_state.student_accounts[student_email]
        interests = student.get('field', [])
        
        recommended_comps = []
        recommended_portfolios = []

        # Recommend competitions matching student fields
        if 'competitions' in st.session_state:
            for c in st.session_state.competitions:
                if c.get("field") in interests:
                    recommended_comps.append(c['title'])
        # Recommend portfolios in fields of interest
        if 'portfolios' in st.session_state:
            for email, projects in st.session_state.portfolios.items():
                for proj in projects:
                    if proj.get("field") in interests:
                        recommended_portfolios.append(f"{proj['title']} by {st.session_state.student_accounts.get(email,{}).get('name','Unknown')}")

        st.markdown("**Recommended Competitions:**")
        st.write(recommended_comps if recommended_comps else "No recommendations yet.")
        st.markdown("**Recommended Portfolios:**")
        st.write(recommended_portfolios if recommended_portfolios else "No recommendations yet.")
    else:
        st.info("No student accounts found. Create an account first.")

# =======================
# Tab 2: Mentor Feedback
# =======================
with tab2:
    st.markdown("### Mentor Feedback / Competition Scoring")
    if 'competitions' in st.session_state:
        selected_comp = st.selectbox("Select a competition to give feedback", [c['title'] for c in st.session_state.competitions], key="mentor_feedback_comp")
        feedback_text = st.text_area("Enter your feedback or score")
        mentor_name = st.text_input("Your name")
        if st.button("Submit Feedback"):
            if 'mentor_feedback' not in st.session_state:
                st.session_state.mentor_feedback = {}
            if selected_comp not in st.session_state.mentor_feedback:
                st.session_state.mentor_feedback[selected_comp] = []
            st.session_state.mentor_feedback[selected_comp].append({
                "mentor": mentor_name,
                "feedback": feedback_text
            })
            st.success(f"Feedback submitted for {selected_comp}.")

    # Display feedback
    if 'mentor_feedback' in st.session_state and selected_comp in st.session_state.mentor_feedback:
        st.markdown(f"#### Feedback for {selected_comp}")
        for fb in st.session_state.mentor_feedback[selected_comp]:
            st.markdown(f"- **{fb['mentor']}**: {fb['feedback']}")

# =======================
# Tab 3: Portfolio Export
# =======================
with tab3:
    st.markdown("### Export Your Portfolio as PDF")
    student_email = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()) if 'student_accounts' in st.session_state else [], key="export_email")
    if student_email in st.session_state.portfolios:
        projects = st.session_state.portfolios[student_email]

        if st.button("Download Portfolio PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"{st.session_state.student_accounts[student_email]['name']}'s Portfolio", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            for proj in projects:
                pdf.ln(5)
                pdf.multi_cell(0, 10, f"Title: {proj['title']}\nField: {proj.get('field','N/A')}\nDescription: {proj['description']}")
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button("Download PDF", data=pdf_buffer, file_name="portfolio.pdf", mime="application/pdf")
    else:
        st.info("No projects found for this student.")

# =======================
# Tab 4: Integration
# =======================
with tab4:
    st.markdown("### Integration / Notifications")
    st.info("Integration with Slack, Discord, or Teams can be added via webhooks. This is a placeholder for future implementation.")
    st.text("Example: Send notification to a Slack channel when a competition receives a new submission.")

# =======================
# Tab 5: Gamified Challenges
# =======================
with tab5:
    st.markdown("### Weekly Field-Specific Mini Challenges")
    if 'gamified_challenges' not in st.session_state:
        st.session_state.gamified_challenges = {
            "AI": ["Build a mini AI chatbot", "Submit a Python ML script"],
            "Math": ["Solve 5 advanced math problems", "Create a math visualization project"],
            "Business": ["Create a marketing plan", "Submit a business case study"]
        }

    selected_field = st.selectbox("Select your field", list(st.session_state.gamified_challenges.keys()), key="gamified_field")
    st.markdown("**Challenges:**")
    for challenge in st.session_state.gamified_challenges[selected_field]:
        st.markdown(f"- {challenge}")
    st.info("Completing challenges can earn badges (to be implemented).")
# -----------------------------
# Add-On: Notifications & Engagement
# -----------------------------
st.markdown("---")
st.subheader("Notifications & Engagement")

# Initialize notifications & XP
if 'notifications' not in st.session_state:
    st.session_state.notifications = {}  # {email: [messages]}
if 'student_accounts' not in st.session_state:
    st.session_state.student_accounts = {}  # Ensure accounts exist
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = {}  # {email: XP}

# --- Helper Functions ---
def add_notification(email, message):
    if email not in st.session_state.notifications:
        st.session_state.notifications[email] = []
    st.session_state.notifications[email].append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def add_xp(email, points):
    if email not in st.session_state.xp_points:
        st.session_state.xp_points[email] = 0
    st.session_state.xp_points[email] += points
    # Update in account profile if exists
    if email in st.session_state.student_accounts:
        st.session_state.student_accounts[email]['xp'] = st.session_state.xp_points[email]

# =======================
# Example Triggers
# =======================
# 1. Portfolio Vote
if 'portfolio_votes' in st.session_state:
    for email, votes in st.session_state.portfolio_votes.items():
        # Add notification and XP
        add_notification(email, f"Your portfolio has {votes} votes.")
        add_xp(email, votes)  # 1 XP per vote

# 2. New Submission
if 'competition_submissions' in st.session_state:
    for comp_title, submissions in st.session_state.competition_submissions.items():
        for submission in submissions:
            submitter_email = submission.get("submitter_email")
            add_notification(submitter_email, f"You submitted '{submission['title']}' to '{comp_title}'.")
            add_xp(submitter_email, 5)  # 5 XP for submission

# 3. Competition Join
if 'participants' in st.session_state:
    for comp_title, users in st.session_state.participants.items():
        for user in users:
            # Find email from name
            email = None
            for e, account in st.session_state.student_accounts.items():
                if account['name'] == user:
                    email = e
            if email:
                add_notification(email, f"You joined the competition '{comp_title}'.")
                add_xp(email, 2)  # 2 XP for joining competition

# =======================
# Display Notifications & XP
# =======================
st.markdown("### Your Notifications & XP")
if 'student_accounts' in st.session_state and st.session_state.student_accounts:
    selected_email = st.selectbox("Select your account to view notifications", list(st.session_state.student_accounts.keys()), key="notif_email")
    
    st.markdown(f"**XP Points:** {st.session_state.xp_points.get(selected_email, 0)}")
    
    user_notifications = st.session_state.notifications.get(selected_email, [])
    if user_notifications:
        st.markdown("**Recent Notifications:**")
        for msg in reversed(user_notifications[-10:]):  # Show last 10 notifications
            st.markdown(f"- {msg}")
    else:
        st.info("No notifications yet.")
# -----------------------------
# Add-On: Enhanced Portfolio System
# -----------------------------
st.markdown("---")
st.subheader("Enhanced Portfolio System")

# Initialize portfolio data structures if not exist
if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {}  # {email: [{"title":..., "field":..., "description":..., "versions":[...], "verified":False, "votes":0, "comments":[]}]}

if 'portfolio_votes' not in st.session_state:
    st.session_state.portfolio_votes = {}  # {email: total_votes}

# --- Submit or Update Portfolio Project ---
st.markdown("### Submit or Update a Portfolio Project")
if 'student_accounts' in st.session_state and st.session_state.student_accounts:
    student_email = st.selectbox("Select your account", list(st.session_state.student_accounts.keys()), key="portfolio_email")
    student_name = st.session_state.student_accounts[student_email]['name']

    with st.form("portfolio_submission_form"):
        proj_title = st.text_input("Project Title")
        proj_desc = st.text_area("Project Description")
        proj_field = st.selectbox("Field", ["AI","Robotics","Design","Science","Math","Business","Art","Other"])
        submit_portfolio = st.form_submit_button("Submit / Update Project")

        if submit_portfolio:
            if proj_title and proj_desc:
                # Initialize student's portfolio if needed
                if student_email not in st.session_state.portfolios:
                    st.session_state.portfolios[student_email] = []

                # Check if project exists for versioning
                existing_proj = None
                for p in st.session_state.portfolios[student_email]:
                    if p['title'] == proj_title:
                        existing_proj = p
                        break

                if existing_proj:
                    # Add new version
                    existing_proj['versions'].append({"description": proj_desc, "field": proj_field, "timestamp": datetime.datetime.now()})
                    st.success(f"Project '{proj_title}' updated with a new version.")
                else:
                    # Create new project
                    new_proj = {
                        "title": proj_title,
                        "field": proj_field,
                        "description": proj_desc,
                        "versions": [{"description": proj_desc, "field": proj_field, "timestamp": datetime.datetime.now()}],
                        "verified": False,
                        "votes": 0,
                        "comments": []
                    }
                    st.session_state.portfolios[student_email].append(new_proj)
                    st.success(f"Project '{proj_title}' submitted.")

# --- Mentor Verification ---
st.markdown("### Mentor / Judge Verification")
mentor_email = st.text_input("Mentor Email (for verification purposes)")
if st.button("Verify a Project"):
    if mentor_email and 'student_accounts' in st.session_state:
        # Select student and project
        verify_student_email = st.selectbox("Select student", list(st.session_state.student_accounts.keys()), key="verify_student")
        if verify_student_email in st.session_state.portfolios:
            proj_titles = [p['title'] for p in st.session_state.portfolios[verify_student_email]]
            selected_proj_title = st.selectbox("Select project to verify", proj_titles, key="verify_proj")
            # Mark as verified
            for p in st.session_state.portfolios[verify_student_email]:
                if p['title'] == selected_proj_title:
                    p['verified'] = True
                    st.success(f"Project '{selected_proj_title}' verified by mentor {mentor_email}!")

# --- Portfolio Voting & Comments ---
st.markdown("### Portfolio Voting & Feedback")

if 'student_accounts' in st.session_state and 'portfolios' in st.session_state:
    for email, projects in st.session_state.portfolios.items():
        student_name = st.session_state.student_accounts.get(email, {}).get('name', 'Unknown')
        for proj in projects:  # <-- Make sure this loop exists
            st.markdown(f"**{proj['title']}** by {student_name} ({proj['field']})")
            st.markdown(f"{proj['description']}")
            
            if proj.get('verified'):
                st.markdown("✅ Verified")
            
            # Voting
            vote = st.radio(f"Vote for {proj['title']}", ["No", "Yes"], key=f"vote_{email}_{proj['title']}")
            if st.button(f"Submit Vote for {proj['title']}", key=f"vote_btn_{email}_{proj['title']}"):
                if vote == "Yes":
                    proj['votes'] += 1
                    st.success(f"You voted for {proj['title']}")
                    # Increment total portfolio votes for account
                    if email not in st.session_state.portfolio_votes:
                        st.session_state.portfolio_votes[email] = 0
                    st.session_state.portfolio_votes[email] += 1

            # Commenting
            comment_text = st.text_input(f"Leave a comment for {proj['title']}", key=f"comment_{email}_{proj['title']}")
            if st.button(f"Submit Comment for {proj['title']}", key=f"comment_btn_{email}_{proj['title']}"):
                if comment_text:
                    if 'comments' not in proj:
                        proj['comments'] = []
                    proj['comments'].append(comment_text)
                    st.success("Comment submitted.")

            # Average votes
            st.markdown(f"⭐ Votes: {proj.get('votes',0)}")
# -----------------------------
# Add-On: Portfolio Badges Display
# -----------------------------
st.markdown("---")
st.subheader("Portfolio Badges & Awards")

# Ensure necessary structures exist
if 'student_accounts' not in st.session_state:
    st.session_state.student_accounts = {}

if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {}

if 'badges' not in st.session_state:
    st.session_state.badges = {}  # {email: ["Badge1", "Badge2"]}

# --- Assign example badges from competitions (Top 3 / Verified / Gamified) ---
# You can also dynamically generate badges based on votes, verification, challenges, etc.
for email, projects in st.session_state.portfolios.items():
    account = st.session_state.student_accounts.get(email)
    if account:
        # Initialize badges in account if not exists
        if 'badges' not in account:
            account['badges'] = []

        # Example: verified project badge
        for proj in projects:
            if proj.get('verified') and "Verified Project" not in account['badges']:
                account['badges'].append(f"✅ Verified Project: {proj['title']}")

            # Example: top 3 competition badge (assumes st.session_state.competition_votes exists)
            if 'competition_votes' in st.session_state:
                for comp_title, votes_list in st.session_state.competition_votes.items():
                    # Check if this student is top 3
                    sorted_votes = sorted(votes_list, key=lambda x: x['votes'], reverse=True)[:3]
                    for i, winner in enumerate(sorted_votes):
                        if winner['email'] == email:
                            badge_name = f"🏆 Top {i+1} in {comp_title}"
                            if badge_name not in account['badges']:
                                account['badges'].append(badge_name)

# --- Display portfolios with badges ---
if st.session_state.student_accounts:
    selected_email = st.selectbox("Select a student to view portfolio and badges", list(st.session_state.student_accounts.keys()))
    account = st.session_state.student_accounts[selected_email]
    st.markdown(f"### {account['name']}'s Portfolio & Badges")

    # Display badges earned
    if 'badges' in account and account['badges']:
        st.markdown("**Badges / Achievements:**")
        for b in account['badges']:
            st.markdown(f"- {b}")
    else:
        st.markdown("No badges earned yet.")

    # Display portfolio projects
    if selected_email in st.session_state.portfolios:
        for proj in st.session_state.portfolios[selected_email]:
            st.markdown(f"**{proj['title']}** ({proj.get('field','No field')})")
            st.markdown(f"{proj['description']}")
            if proj.get('verified'):
                st.markdown("✅ Verified")
            # Show comments if exist
            if proj.get('comments'):
                st.markdown("**Comments:**")
                for c in proj['comments']:
                    st.markdown(f"- {c}")
            # Show votes
            st.markdown(f"⭐ Votes: {proj.get('votes',0)}")
# -----------------------------
# Add-On: Enhanced Badges with Date, Icons & Filtering
# -----------------------------
st.markdown("---")
st.subheader("Enhanced Badges with Date, Icons & Filtering")

import datetime

# --- Initialize badges structure if not exists ---
for email, account in st.session_state.student_accounts.items():
    if 'badges' not in account:
        account['badges'] = []  # Each badge will now be a dict with name, date, icon, activity_type

# --- Example badge icons ---
badge_icons = {
    "Verified Project": "✅",
    "Top 1 in Competition": "🥇",
    "Top 2 in Competition": "🥈",
    "Top 3 in Competition": "🥉",
    "Multi-Field Participant": "🌟",
    "Gamified Challenge": "🎮",
    "First Portfolio Submitted": "🏆"
}

# --- Assign badges with date & icon if not already ---
for email, projects in st.session_state.portfolios.items():
    account = st.session_state.student_accounts.get(email)
    if account:
        # Verified projects
        for proj in projects:
            badge_name = f"Verified: {proj['title']}"
            if proj.get('verified') and not any(b['name'] == badge_name for b in account['badges']):
                account['badges'].append({
                    "name": badge_name,
                    "date_awarded": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "icon": badge_icons.get("Verified Project","✅"),
                    "activity": "Verification"
                })

        # Top 3 competitions
        if 'competition_votes' in st.session_state:
            for comp_title, votes_list in st.session_state.competition_votes.items():
                sorted_votes = sorted(votes_list, key=lambda x: x['votes'], reverse=True)[:3]
                for i, winner in enumerate(sorted_votes):
                    if winner['email'] == email:
                        badge_name = f"Top {i+1} in {comp_title}"
                        if not any(b['name'] == badge_name for b in account['badges']):
                            icon_key = f"Top {i+1} in Competition"
                            account['badges'].append({
                                "name": badge_name,
                                "date_awarded": datetime.datetime.now().strftime("%Y-%m-%d"),
                                "icon": badge_icons.get(icon_key, "🏆"),
                                "activity": "Competition"
                            })

# --- Filter Portfolios by Badge ---
st.markdown("### Filter Portfolios by Badge")
all_badge_types = ["All"] + list(set(b['activity'] for a in st.session_state.student_accounts.values() for b in a.get('badges',[])))
selected_filter = st.selectbox("Select badge filter", all_badge_types)

# --- Display portfolios with filtered badges ---
for email, projects in st.session_state.portfolios.items():
    account = st.session_state.student_accounts.get(email)
    if not account:
        continue
    # Check if any badge matches filter
    if selected_filter != "All":
        badge_matches = any(b['activity'] == selected_filter for b in account.get('badges',[]))
        if not badge_matches:
            continue

    st.markdown(f"### {account['name']}'s Portfolio")
    
    # Display badges
    if account.get('badges'):
        st.markdown("**Badges / Achievements:**")
        for b in account['badges']:
            if selected_filter != "All" and b['activity'] != selected_filter:
                continue
            st.markdown(f"{b['icon']} {b['name']} (Awarded: {b['date_awarded']}) [{b['activity']}]")
    else:
        st.markdown("No badges earned yet.")

    # Display projects
    for proj in projects:
        st.markdown(f"**{proj['title']}** ({proj.get('field','No field')})")
        st.markdown(f"{proj['description']}")
        if proj.get('verified'):
            st.markdown("✅ Verified")
        if proj.get('comments'):
            st.markdown("**Comments:**")
            for c in proj['comments']:
                st.markdown(f"- {c}")
        st.markdown(f"⭐ Votes: {proj.get('votes',0)}")
# -----------------------------
# Add-On: Weekly Newsletter Tab
# -----------------------------
st.markdown("---")
st.subheader("Special Feature: Weekly Newsletter")

# Create tabs for main interface
tab1, tab2, tab3 = st.tabs(["Portfolio & Badges", "Competitions", "Weekly Newsletter"])

# --- Weekly Newsletter Tab ---
with tab3:
    st.markdown("### Weekly Competition Winners & Featured Projects")

    import io
    from fpdf import FPDF

    # Prepare newsletter content
    newsletter_content = []

    if 'competition_votes' in st.session_state and st.session_state.competition_votes:
        for comp_title, votes_list in st.session_state.competition_votes.items():
            # Top 3 winners
            sorted_votes = sorted(votes_list, key=lambda x: x['votes'], reverse=True)[:3]
            if sorted_votes:
                st.markdown(f"#### {comp_title}")
                for i, winner in enumerate(sorted_votes):
                    email = winner['email']
                    votes = winner['votes']
                    student = st.session_state.student_accounts.get(email, {"name":"Unknown"})
                    proj_title = "Unknown Project"
                    if email in st.session_state.portfolios:
                        proj_title = st.session_state.portfolios[email][0]['title']
                    rank = f"{i+1}{['st','nd','rd'][i] if i<3 else 'th'} Place"
                    st.markdown(f"🏆 {rank}: {proj_title} by {student['name']} ({email}) | Votes: {votes}")

                    newsletter_content.append({
                        "competition": comp_title,
                        "rank": rank,
                        "project": proj_title,
                        "student_name": student['name'],
                        "email": email,
                        "votes": votes
                    })
    else:
        st.info("No competition votes yet this week.")

    # --- Download PDF Button ---
    if newsletter_content:
        st.markdown("---")
        st.markdown("### Download Newsletter PDF")
        if st.button("Download Weekly Newsletter PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "FusionX Weekly Competition Newsletter", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(5)
            for entry in newsletter_content:
                pdf.multi_cell(0, 10,
                    f"Competition: {entry['competition']}\n"
                    f"Rank: {entry['rank']}\n"
                    f"Project: {entry['project']}\n"
                    f"Student: {entry['student_name']} ({entry['email']})\n"
                    f"Votes: {entry['votes']}\n\n"
                )
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button("Download PDF", data=pdf_buffer, file_name="weekly_newsletter.pdf", mime="application/pdf")
# -----------------------------
# Add-On: Top Header Bar for Fusion Home Page
# -----------------------------
st.markdown(
    """
    <style>
    /* Full-width top header */
    .fusionx-topbar {
        position: fixed; /* Stick to the very top */
        top: 0;
        left: 0;
        width: 100%;
        background-color: #4B0082; /* Dark purple */
        color: white;
        padding: 20px 40px;
        font-size: 28px;
        font-weight: bold;
        display: flex;
        justify-content: flex-end; /* Text/logo on the right */
        align-items: center;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* Optional shadow */
    }

    /* Push main content below the header */
    .stApp > div:first-child {
        margin-top: 80px; /* height of header + some spacing */
    }
    </style>

    <div class="fusionx-topbar">
        FusionX
    </div>
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Add-On: Colorful Sidebar Buttons
# -----------------------------
import streamlit as st

# Initialize current page
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Function to change page
def set_page(page_name):
    st.session_state.current_page = page_name

# Sidebar title
st.sidebar.markdown("## FusionX Navigation")

# Add CSS for colorful buttons
st.sidebar.markdown(
    """
    <style>
    .sidebar-button {
        width: 100%;
        border: none;
        padding: 12px;
        margin: 5px 0;
        border-radius: 12px;
        font-size: 16px;
        font-weight: bold;
        color: white;
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .sidebar-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.3);
    }
    .home { background-color: #6A5ACD; }      /* Slate Blue */
    .propose { background-color: #FF4500; }   /* OrangeRed */
    .pending { background-color: #32CD32; }   /* LimeGreen */
    .portfolio { background-color: #1E90FF; } /* DodgerBlue */
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar buttons (replacing radio links)
if st.sidebar.button("Home", key="home_btn", help="Go to Home"):
    set_page("Home")
if st.sidebar.button("Propose Competition", key="propose_btn", help="Propose a new competition"):
    set_page("Propose Competition")
if st.sidebar.button("Pending Competitions", key="pending_btn", help="See pending competitions"):
    set_page("Pending Competitions")
if st.sidebar.button("Portfolios", key="portfolio_btn", help="View student portfolios"):
    set_page("Portfolios")

# --- Main content based on current_page ---
if st.session_state.current_page == "Home":
    st.header("Home Page")
elif st.session_state.current_page == "Propose Competition":
    st.header("Propose Competition")
elif st.session_state.current_page == "Pending Competitions":
    st.header("Pending Competitions")
elif st.session_state.current_page == "Portfolios":
    st.header("Portfolios")
