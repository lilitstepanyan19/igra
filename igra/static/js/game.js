function getCookie(name) {
    return document.cookie.split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1];
}

const csrftoken = getCookie('csrftoken');
const letters = document.querySelectorAll(".letter");
const game = document.getElementById("game");
const MISS_URL = game.dataset.missUrl;

let speed = 1.5;
let time = 5;

letters.forEach(letter => {
    letter.x = Math.random() * 500;
    letter.y = Math.random() * 300;
    letter.vx = (Math.random() - 0.5) * speed;
    letter.vy = (Math.random() - 0.5) * speed;

    letter.onclick = () => {
        fetch("", {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken }
        }).then(() => location.reload());
    };
});

function move() {
    letters.forEach(l => {
        l.x += l.vx;
        l.y += l.vy;

        if (l.x < 0 || l.x > 500) l.vx *= -1;
        if (l.y < 0 || l.y > 300) l.vy *= -1;

        l.style.left = l.x + "px";
        l.style.top = l.y + "px";
    });
    requestAnimationFrame(move);
}

move();

/* ⏱ таймер */
let gameOver = false;

const timerId = setInterval(() => {
    if (gameOver) return;

    time--;
    document.getElementById("time").innerText = time;

    if (time <= 0) {
        gameOver = true;          // ⛔ стоп
        clearInterval(timerId);  // ⛔ стоп таймер

        fetch(MISS_URL, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            }
        }).then(() => location.reload());
    }
}, 1000);


