
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'fi-nder-demo'

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
OPPS_FILE = os.path.join(os.path.dirname(__file__), 'opportunities.json')


from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = 'fi-nder-demo'

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
OPPS_FILE = os.path.join(os.path.dirname(__file__), 'opportunities.json')
# --- API for Applicants Modal ---
# Get applicants for an opportunity (with user info and status)
@app.route('/get-applicants/<int:opp_id>')
def get_applicants_api(opp_id):
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    opps = get_opportunities()
    opp = next((o for o in opps if o['id'] == opp_id and o.get('createdBy') == user['email']), None)
    if not opp:
        return jsonify({'success': False, 'error': 'Opportunity not found or not authorized'}), 404
    applicants = []
    users = get_users()
    for email in opp.get('applicants', []):
        u = next((x for x in users if x['email'].lower() == email.lower()), None)
        applicants.append({
            'email': email,
            'name': u['name'] if u else email,
            'profile': u['profile'] if u else '',
            'skills': u['mo'] if u else '',
            'status': opp.get('applicants_status', {}).get(email, 'Pending')
        })
    return jsonify({'success': True, 'applicants': applicants})

# Update applicant status (Accept/Reject)
@app.route('/update-applicant-status/<int:opp_id>', methods=['POST'])
def update_applicant_status_api(opp_id):
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = request.get_json()
    email = data.get('email')
    status = data.get('status')
    if not email or status not in ['Accepted', 'Rejected']:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    opps = get_opportunities()
    opp = next((o for o in opps if o['id'] == opp_id and o.get('createdBy') == user['email']), None)
    if not opp:
        return jsonify({'success': False, 'error': 'Opportunity not found or not authorized'}), 404
    if 'applicants_status' not in opp:
        opp['applicants_status'] = {}
    opp['applicants_status'][email] = status
    save_opportunities(opps)
    return jsonify({'success': True})

# Edit opportunity route
@app.route('/edit-opportunity/<int:opp_id>', methods=['GET', 'POST'])
def edit_opportunity(opp_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    opps = get_opportunities()
    opp = next((o for o in opps if o['id'] == opp_id and o.get('createdBy') == user['email']), None)
    if not opp:
        flash('Opportunity not found or not authorized.')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        opp['title'] = request.form['title']
        opp['role'] = ', '.join(request.form.getlist('role'))
        opp['team'] = request.form['team']
        opp['duration'] = request.form['duration']
        opp['commitment'] = request.form['commitment']
        opp['start_date'] = request.form['start_date']
        opp['skills'] = request.form['skills']
        opp['openings'] = int(request.form['openings'])
        save_opportunities(opps)
        flash('Opportunity updated!')
        return redirect(url_for('home'))
    # For GET, show edit form with pre-filled data
    return render_template('main.html', user=user, opp=opp, applied=[], created=[], opportunities=[], active_tab='edit')

# Close opportunity route
@app.route('/end-opportunity/<int:opp_id>', methods=['POST'])
def end_opportunity(opp_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    opps = get_opportunities()
    opp = next((o for o in opps if o['id'] == opp_id and o.get('createdBy') == user['email']), None)
    if not opp:
        flash('Opportunity not found or not authorized.')
        return redirect(url_for('home'))
    opp['status'] = 'Closed'
    save_opportunities(opps)
    flash('Opportunity closed!')
    return redirect(url_for('home'))


# Utility functions for file-based storage
def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def get_opportunities():
    if not os.path.exists(OPPS_FILE):
        return []
    with open(OPPS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_opportunities(opps):
    with open(OPPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(opps, f, indent=2)

def get_user_by_email(email):
    users = get_users()
    for u in users:
        if u['email'].lower() == email.lower():
            return u
    return None

@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html', show_signup=False, error=None, email=None)


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    user = get_user_by_email(email)
    if user:
        session['user'] = user
        return redirect(url_for('home'))
    else:
        return render_template('login.html', show_signup=True, error='Email not found. Please sign up.', email=email)


@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name'].strip()
    email = request.form['email'].strip().lower()
    profile = request.form['profile'].strip()
    mo = request.form['mo'].strip()
    users = get_users()
    if any(u['email'].lower() == email for u in users):
        return render_template('login.html', show_signup=True, error='Email already exists.', email=email)
    user = {"name": name, "email": email, "profile": profile, "mo": mo}
    users.append(user)
    save_users(users)
    session['user'] = user
    return redirect(url_for('home'))


@app.route('/home')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    opportunities = get_opportunities()
    applied = [o for o in opportunities if 'applicants' in o and user['email'] in o['applicants']]
    created = [o for o in opportunities if o.get('createdBy') == user['email']]
    # Home tab switching
    home_tab = request.args.get('tab', 'created')
    return render_template('main.html', user=user, applied=applied, created=created, opportunities=opportunities, active_tab='home', home_tab=home_tab)


# Profile tab
@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    return render_template('main.html', user=user, applied=[], created=[], opportunities=[], active_tab='profile')



@app.route('/create-opportunity', methods=['GET', 'POST'])
def create_opportunity():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        title = request.form['title']
        # Multi-select roles
        role = request.form.getlist('role')
        team = request.form['team']
        duration = int(request.form['duration'])
        commitment = int(request.form['commitment'])
        start_date = request.form['start_date']
        description = request.form['description']
        # Skills from hidden field
        skills = request.form['skills']
        openings = int(request.form['openings'])
        from datetime import datetime
        opps = get_opportunities()
        new_opp = {
            'id': (max([o['id'] for o in opps]) + 1) if opps else 1,
            'title': title,
            'role': ', '.join(role),
            'team': team,
            'duration': duration,
            'commitment': commitment,
            'description': description,
            'start_date': start_date,
            'skills': skills,
            'openings': openings,
            'createdBy': user['email'],
            'createdByName': user['name'],
            'createdAt': datetime.now().strftime('%b %d, %Y %I:%M %p'),
            'applicants': [],
            'status': 'Open'
        }
        opps.append(new_opp)
        save_opportunities(opps)
        flash('Opportunity created!')
        return redirect(url_for('home'))
    return render_template('main.html', user=user, applied=[], created=[], opportunities=[], active_tab='create')

# Apply tab: show all opportunities, latest first
@app.route('/apply')
def apply():
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    opportunities = get_opportunities()
    # Sort by createdAt (latest first)
    from datetime import datetime
    def parse_dt(o):
        try:
            return datetime.strptime(o.get('createdAt',''), '%b %d, %Y %I:%M %p')
        except:
            return datetime.min
    opportunities = sorted(opportunities, key=parse_dt, reverse=True)
    return render_template('main.html', user=user, applied=[], created=[], opportunities=opportunities, active_tab='apply')

# Opportunity details page
@app.route('/opportunity/<int:opp_id>', methods=['GET', 'POST'])
def opportunity_details(opp_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    opps = get_opportunities()
    opp = next((o for o in opps if o['id'] == opp_id), None)
    if not opp:
        flash('Opportunity not found.')
        return redirect(url_for('apply'))
    # Application logic removed: POST requests for apply/not_interested are no longer handled.
    return render_template('opportunity_details.html', user=user, opp=opp)
# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=5000)
