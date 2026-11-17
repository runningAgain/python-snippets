import argparse
import getpass
import sys
import requests

# --- KONFIGURATION ---
BASE_URL = "https://beispiel.de"
LOGIN_ENDPOINT = "/login"
DATA_ENDPOINT = "/data"

# Setze dies auf False, falls deine API "application/x-www-form-urlencoded" 
# statt "application/json" beim Login erwartet:
USE_JSON_BODY = True 
# ---------------------


def get_credentials():
    """Liest Benutzername und Passwort über Parameter oder einen sicheren Prompt ein."""
    parser = argparse.ArgumentParser(description="REST API Login und Datenabfrage")
    parser.add_argument("-u", "--username", help="Benutzername für die API")
    parser.add_argument("-p", "--password", help="Passwort für die API")
    args = parser.parse_args()

    username = args.username or input("Benutzername: ")
    password = args.password or getpass.getpass("Passwort: ")

    return username, password


def login(username, password):
    """Sendet einen POST-Request mit Credentials im Body und extrahiert das Token."""
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    
    # Passe die Keys ("username", "password") an, falls deine API z.B. "user" oder "email" erwartet
    payload = {
        "username": username,
        "password": password
    }

    try:
        if USE_JSON_BODY:
            # Sendet als JSON (Content-Type: application/json)
            response = requests.post(login_url, json=payload, timeout=10)
        else:
            # Sendet als Form-Daten (Content-Type: application/x-www-form-urlencoded)
            response = requests.post(login_url, data=payload, timeout=10)

        response.raise_for_status()
        
        data = response.json()
        # Passe den Key an die Antwort deiner API an (z. B. "token", "sessionToken", "access_token")
        token = data.get("token") or data.get("access_token") or data.get("sessionToken")
        
        if not token:
            print(f"Fehler: Kein Token in der Antwort gefunden. Antwort war: {data}", file=sys.stderr)
            sys.exit(1)
            
        return token

    except requests.exceptions.RequestException as e:
        print(f"Login fehlgeschlagen: {e}", file=sys.stderr)
        # Gibt bei einem HTTP-Fehler (z.B. 400 oder 401) auch die Antwort des Servers aus:
        if e.response is not None:
            print(f"Server-Details: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def fetch_data(token):
    """Fragt Daten mit dem erhaltenen Session-Token im Header ab."""
    data_url = f"{BASE_URL}{DATA_ENDPOINT}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(data_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Datenabfrage fehlgeschlagen: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Server-Details: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def main():
    username, password = get_credentials()
    
    print("Sende Login-POST...")
    token = login(username, password)
    print("Login erfolgreich! Token erhalten.")

    print("Frage API-Daten ab...")
    result = fetch_data(token)
    print("Ergebnis:")
    print(result)


if __name__ == "__main__":
    main()
