from flask import Flask, render_template, jsonify
import requests
import random
import threading
import time

app = Flask(__name__)

PLACE_ID = 98664161516921

# Cache server
cached_servers = []

# Simpan beberapa server terakhir
last_servers = []

# Maksimal history server
MAX_HISTORY = 5

# Refresh cache tiap 30 detik
REFRESH_INTERVAL = 30

# Maximum halaman API
MAX_PAGES = 2

# Maximum retry API
MAX_API_RETRY = 3

# Maximum retry random
MAX_RANDOM_RETRY = 15


@app.route('/')
def index():
    return render_template('index.html')


# =========================================
# FETCH SERVER ROBLOX
# =========================================
def fetch_servers():

    global cached_servers

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    temp_servers = []

    cursor = None

    try:

        for _ in range(MAX_PAGES):

            url = (
                f"https://games.roblox.com/v1/games/"
                f"{PLACE_ID}/servers/Public"
                f"?sortOrder=Desc"
                f"&limit=100"
            )

            # Pagination
            if cursor:
                url += f"&cursor={cursor}"

            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            data = response.json()

            servers = data.get("data", [])

            # Filter server valid
            filtered_servers = [

                server for server in servers

                if (

                    server.get('playing', 0) >= 1

                    and

                    server.get('playing', 0)
                    < server.get('maxPlayers', 0)

                    and

                    server.get('playing', 0) <= 11
                )
            ]

            temp_servers.extend(filtered_servers)

            cursor = data.get("nextPageCursor")

            if not cursor:
                break

        # Acak total server
        random.shuffle(temp_servers)

        # Update cache
        if temp_servers:
            cached_servers = temp_servers

            print(
                f"[CACHE UPDATED] "
                f"{len(cached_servers)} servers loaded"
            )

    except Exception as e:

        print(f"[FETCH ERROR] {e}")


# =========================================
# AUTO REFRESH CACHE
# =========================================
def background_updater():

    while True:

        fetch_servers()

        time.sleep(REFRESH_INTERVAL)


# =========================================
# RANDOM SERVER
# =========================================
@app.route('/random-server')
def random_server():

    global last_servers

    # Jika cache kosong
    if not cached_servers:

        # Retry fetch manual
        for _ in range(MAX_API_RETRY):

            fetch_servers()

            if cached_servers:
                break

            time.sleep(1)

    # Masih kosong
    if not cached_servers:

        return jsonify({

            'success': False,

            'message': 'Tidak ada server tersedia'

        })

    selected_server = None

    retry_count = 0

    # Cari server yang belum pernah dipakai
    while retry_count < MAX_RANDOM_RETRY:

        server = random.choice(cached_servers)

        server_id = server['id']

        if server_id not in last_servers:

            selected_server = server

            break

        retry_count += 1

    # Fallback
    if not selected_server:

        selected_server = random.choice(cached_servers)

    server_id = selected_server['id']

    # Simpan history server
    last_servers.append(server_id)

    # Batasi history
    if len(last_servers) > MAX_HISTORY:
        last_servers.pop(0)

    roblox_url = (
        f"roblox://placeId={PLACE_ID}"
        f"&gameInstanceId={server_id}"
    )

    return jsonify({

        'success': True,

        'server_id': server_id,

        'playing': selected_server['playing'],

        'maxPlayers': selected_server['maxPlayers'],

        'join_url': roblox_url,

        'cached_servers': len(cached_servers),

        'retry_count': retry_count

    })


# =========================================
# START BACKGROUND THREAD
# =========================================
threading.Thread(
    target=background_updater,
    daemon=True
).start()


# =========================================
# RUN APP
# =========================================
if __name__ == '__main__':

    # Fetch pertama saat app start
    fetch_servers()

    app.run(
        debug=True,
        port=5000
    )