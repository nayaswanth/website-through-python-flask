<<<<<<< HEAD
import requests

BACKEND_URL = "http://localhost:3001"

# Example: Get all users
def get_users():
    resp = requests.get(f"{BACKEND_URL}/users")
    if resp.ok:
        return resp.json()
    else:
        print("Failed to fetch users:", resp.text)
        return []

# Example: Register a new user
def register_user(email, name, role, skills):
    data = {"email": email, "name": name, "role": role, "skills": skills}
    resp = requests.post(f"{BACKEND_URL}/users", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Registration failed:", resp.text)
        return None

# Example: Get all opportunities
def get_opportunities():
    resp = requests.get(f"{BACKEND_URL}/opportunities")
    if resp.ok:
        return resp.json()
    else:
        print("Failed to fetch opportunities:", resp.text)
        return []

# Example: Create a new opportunity
def create_opportunity(title, duration, skills, openings, createdBy):
    data = {
        "title": title,
        "duration": duration,
        "skills": skills,
        "openings": openings,
        "createdBy": createdBy
    }
    resp = requests.post(f"{BACKEND_URL}/opportunities", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Failed to create opportunity:", resp.text)
        return None

# Example: Apply to an opportunity
def apply_to_opportunity(opportunityId, userEmail):
    data = {"opportunityId": opportunityId, "userEmail": userEmail}
    resp = requests.post(f"{BACKEND_URL}/apply", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Failed to apply:", resp.text)
        return None

if __name__ == "__main__":
    # Demo usage
    print("All users:", get_users())
    print("All opportunities:", get_opportunities())
    # You can call register_user, create_opportunity, apply_to_opportunity as needed
=======
import requests

BACKEND_URL = "http://localhost:3001"

# Example: Get all users
def get_users():
    resp = requests.get(f"{BACKEND_URL}/users")
    if resp.ok:
        return resp.json()
    else:
        print("Failed to fetch users:", resp.text)
        return []

# Example: Register a new user
def register_user(email, name, role, skills):
    data = {"email": email, "name": name, "role": role, "skills": skills}
    resp = requests.post(f"{BACKEND_URL}/users", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Registration failed:", resp.text)
        return None

# Example: Get all opportunities
def get_opportunities():
    resp = requests.get(f"{BACKEND_URL}/opportunities")
    if resp.ok:
        return resp.json()
    else:
        print("Failed to fetch opportunities:", resp.text)
        return []

# Example: Create a new opportunity
def create_opportunity(title, duration, skills, openings, createdBy):
    data = {
        "title": title,
        "duration": duration,
        "skills": skills,
        "openings": openings,
        "createdBy": createdBy
    }
    resp = requests.post(f"{BACKEND_URL}/opportunities", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Failed to create opportunity:", resp.text)
        return None

# Example: Apply to an opportunity
def apply_to_opportunity(opportunityId, userEmail):
    data = {"opportunityId": opportunityId, "userEmail": userEmail}
    resp = requests.post(f"{BACKEND_URL}/apply", json=data)
    if resp.ok:
        return resp.json()
    else:
        print("Failed to apply:", resp.text)
        return None

if __name__ == "__main__":
    # Demo usage
    print("All users:", get_users())
    print("All opportunities:", get_opportunities())
    # You can call register_user, create_opportunity, apply_to_opportunity as needed
>>>>>>> 7ebebb4bdf3daad564ba3e90fef4ab659b2acf35
