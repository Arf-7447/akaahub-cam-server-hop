let alarmEnabled = false;

let alarmPlaying = false;

const bossAudio = document.getElementById('boss-audio');


// Toggle alarm
function toggleAlarm() {

    const icon = document.getElementById('speaker-icon');

    alarmEnabled = !alarmEnabled;

    if (alarmEnabled) {

        icon.innerText = '🔊';

    } else {

        icon.innerText = '🔇';

        bossAudio.pause();

        bossAudio.currentTime = 0;

        alarmPlaying = false;
    }
}

async function joinRandomServer() {

    const info = document.getElementById('server-info');

    // Reset timer lama jika ada
    if (window.serverInfoTimeout) {
        clearTimeout(window.serverInfoTimeout);
    }

    info.classList.remove('hidden');

    info.innerHTML = `
        <div class="text-yellow-300 animate-pulse">
            Searching random server...
        </div>
    `;

    try {

        const response = await fetch('/random-server');

        const data = await response.json();

        if (!data.success) {

            info.innerHTML = `
                <div class="text-red-400">
                    ${data.message}
                </div>
            `;

            // Auto hide notif error
            window.serverInfoTimeout = setTimeout(() => {

                info.classList.add('hidden');

            }, 15000);

            return;
        }

        info.innerHTML = `
            <div class="space-y-2">

                <div class="text-green-400 text-xl font-bold">
                    Server Found!
                </div>

                <div>
                    Players: ${data.playing}/${data.maxPlayers}
                </div>

                <div class="text-sm break-all text-slate-300">
                    ${data.server_id}
                </div>

            </div>
        `;

        // Auto hide notif setelah 15 detik
        window.serverInfoTimeout = setTimeout(() => {

            info.classList.add('hidden');

        }, 15000);

        // Redirect Roblox
        setTimeout(() => {

            window.location.href = data.join_url;

        }, 1500);

    } catch (error) {

        info.innerHTML = `
            <div class="text-red-400">
                Error: ${error}
            </div>
        `;

        // Auto hide notif error
        window.serverInfoTimeout = setTimeout(() => {

            info.classList.add('hidden');

        }, 15000);
    }
}


function updateBossTimer() {

    const now = new Date();

    const minutes = now.getMinutes();

    const currentQuarter = Math.floor(minutes / 15) * 15;

    // Spawn terakhir
    let spawnTime = new Date(now);

    spawnTime.setMinutes(currentQuarter);
    spawnTime.setSeconds(0);
    spawnTime.setMilliseconds(0);

    // Spawn berikutnya
    let nextSpawn = new Date(spawnTime);

    if (now >= spawnTime) {
        nextSpawn.setMinutes(currentQuarter + 15);
    }

    // Boss hilang setelah 5 menit
    let despawnTime = new Date(spawnTime);

    despawnTime.setMinutes(currentQuarter + 5);

    const nextSpawnElement =
        document.getElementById('next-spawn');

    const despawnElement =
        document.getElementById('despawn-time');

    const statusElement =
        document.getElementById('boss-status');

    const countdownElement =
        document.getElementById('countdown');

    const countdownLabel =
    document.getElementById('countdown-label');

    // FORMAT 24 JAM
    const format24Hour = (date) => {

        const hours = date.getHours()
            .toString()
            .padStart(2, '0');

        const mins = date.getMinutes()
            .toString()
            .padStart(2, '0');

        return `${hours}:${mins}`;
    };

    nextSpawnElement.innerText =
        `Next boss spawn at ${format24Hour(nextSpawn)}`;

    despawnElement.innerText =
        `Boss disappear at ${format24Hour(despawnTime)}`;

    let targetTime;

    // Boss aktif selama 5 menit
    if (now >= spawnTime && now < despawnTime) {

        statusElement.innerText = 'BOSS IS ACTIVE';
    
        statusElement.className =
            'text-lg sm:text-xl font-semibold text-green-400 break-words';
    
        // Dynamic text
        countdownLabel.innerText =
            'until next boss despawn';
    
        targetTime = despawnTime;
    
        // Mainkan alarm jika enabled
        if (alarmEnabled && !alarmPlaying) {
    
            alarmPlaying = true;
    
            bossAudio.play();
    
            setTimeout(() => {
    
                bossAudio.pause();
    
                bossAudio.currentTime = 0;
    
            }, 30000);
        }
    
    } else {
    
        // Reset alarm state
        alarmPlaying = false;
    
        statusElement.innerText = 'Waiting Boss Spawn';
    
        statusElement.className =
            'text-lg sm:text-xl font-semibold text-yellow-300 break-words';
    
        // Dynamic text
        countdownLabel.innerText =
            'until next boss spawn';
    
        targetTime = nextSpawn;
    }

    // Countdown
    const diff = targetTime - now;

    const totalSeconds = Math.floor(diff / 1000);

    const mins = Math.floor(totalSeconds / 60)
        .toString()
        .padStart(2, '0');

    const secs = (totalSeconds % 60)
        .toString()
        .padStart(2, '0');

    countdownElement.innerText = `${mins}:${secs}`;
}

setInterval(updateBossTimer, 1000);

updateBossTimer();