from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = 'fi-nder-demo'

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
OPPS_FILE = os.path.join(os.path.dirname(__file__), 'opportunities.json')


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
    users = get_users()
    applied = [o for o in opportunities if 'applicants' in o and user['email'] in o['applicants']]
    created = [o for o in opportunities if o.get('createdBy') == user['email']]
    # Home tab switching
    home_tab = request.args.get('tab', 'created')
    return render_template('main.html', user=user, applied=applied, created=created, opportunities=opportunities, active_tab='home', home_tab=home_tab, users=users)


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
        description = request.form['description']
        role = request.form.getlist('role')
        team = request.form['team']
        duration = int(request.form['duration'])
        commitment = int(request.form['commitment'])
        start_date = request.form['start_date']
        skills = request.form['skills']
        positions = int(request.form['positions'])
        from datetime import datetime
        opps = get_opportunities()
        new_opp = {
            'id': (max([o['id'] for o in opps]) + 1) if opps else 1,
            'title': title,
            'description': description,
            'role': ', '.join(role),
            'team': team,
            'duration': duration,
            'commitment': commitment,
            'start_date': start_date,
            'skills': skills,
            'positions': positions,
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
    # Handle apply/mark not interested
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'apply':
            if user['email'] not in opp['applicants']:
                opp['applicants'].append(user['email'])
                opp['status'] = 'Applied'
                save_opportunities(opps)
                flash('Applied successfully!')
        elif action == 'not_interested':
            if user['email'] in opp['applicants']:
                opp['applicants'].remove(user['email'])
            opp['status'] = 'Not Interested'
            save_opportunities(opps)
            flash('Marked as not interested.')
        return redirect(url_for('opportunity_details', opp_id=opp_id))
    return render_template('opportunity_details.html', user=user, opp=opp)
# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/update-status/<int:opp_id>', methods=['POST'])
def update_status(opp_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login_page'))
    status = request.form.get('status')
    opps = get_opportunities()
    updated = False
    for o in opps:
        if o['id'] == opp_id and o.get('createdBy') == user['email']:
            o['status'] = status
            updated = True
            break
    if updated:
        save_opportunities(opps)
        flash(f'Status updated to {status}.')
    else:
        flash('Opportunity not found or not authorized.')
    return redirect(url_for('home', tab='created'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
