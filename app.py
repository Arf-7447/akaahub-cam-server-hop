from flask import Flask, render_template, jsonify
import requests
import random

app = Flask(__name__)

PLACE_ID = 98664161516921

# Menyimpan server terakhir
last_server_id = None

# Jumlah retry maksimum
MAX_RETRIES = 10


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/random-server')
def random_server():

    global last_server_id

    url = (
        f"https://games.roblox.com/v1/games/"
        f"{PLACE_ID}/servers/Public"
        f"?sortOrder=Asc&limit=100"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(url, headers=headers)

        data = response.json()

        servers = data.get("data", [])

        # Filter server yang belum penuh
        available_servers = [

            server for server in servers

            if (
                server['playing'] < server['maxPlayers']
                and
                server['playing'] >= 1
            )
        ]

        if not available_servers:

            return jsonify({

                'success': False,

                'message': 'Tidak ada server tersedia'

            })

        selected_server = None

        retry_count = 0

        # Auto retry cari server berbeda
        while retry_count < MAX_RETRIES:

            random_server_choice = random.choice(available_servers)

            server_id = random_server_choice['id']

            # Hindari server yang sama
            if server_id != last_server_id:

                selected_server = random_server_choice

                break

            retry_count += 1

        # Jika gagal menemukan server berbeda
        if not selected_server:

            selected_server = random.choice(available_servers)

        server_id = selected_server['id']

        # Simpan server terakhir
        last_server_id = server_id

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

            'retry_count': retry_count

        })

    except Exception as e:

        return jsonify({

            'success': False,

            'message': str(e)

        })


if __name__ == '__main__':

    app.run(
        debug=True,
        port=5000
    )