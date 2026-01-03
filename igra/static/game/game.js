const lettersContainer = document.getElementById("letters");
const countEl = document.getElementById("count");
const portal = document.getElementById("portal");
const portal2 = document.getElementById("portal2");
const baby = document.getElementById("baby");
const resetBtn = document.getElementById("resetBtn");
const world2 = document.getElementById("world2");
const crystalsWrap = document.getElementById("crystals");
const crystalCountEl = document.getElementById("crystalCount");
let crystalsCollected = 0;
const letters = ["A", "B", "C", "D", "E"];

window.addEventListener('DOMContentLoaded', () => {
    portal.classList.add('hidden');
    portal2.classList.add('hidden');
    world2.classList.add('hidden');

    // создаём буквы после загрузки DOM
    letters.forEach(l => {
        const el = document.createElement("div");
        el.className = "letter";
        el.textContent = l;
        el.onclick = () => eatLetter(el);
        lettersContainer.appendChild(el);
    });
});

resetBtn.onclick = () => {
    fetch('/api/reset/', { method: 'POST' }).then(() => location.reload());
};
// resetBtn.onclick = () => {
//     // Сброс букв
//     document.querySelectorAll('.letter').forEach(l => l.classList.remove('eaten'));
//     document.getElementById('count').textContent = 0;

//     // Скрываем порталы
//     document.getElementById('portal').classList.add('hidden');
//     document.getElementById('portal2').classList.add('hidden');

//     // Показываем главный экран и скрываем миры
//     document.querySelector('.game').style.display = 'block';
//     document.getElementById('world').classList.add('hidden');
//     document.getElementById('world2').classList.add('hidden');

//     // Сбрасываем кристаллы
//     document.querySelectorAll('.crystal').forEach(c => c.remove());
//     document.getElementById('crystalCount').textContent = 0;
//     crystalsCollected = 0;

//     // Сбрасываем малыша
//     document.getElementById('baby').style.transform = "scale(1)";
// };


function eatLetter(el) {
    fetch('/api/eat/')
        .then(res => res.json())
        .then(data => {
            if (!data || !data.letters) return;  // защита от пустого ответа
            el.classList.add('eaten');
            countEl.textContent = data.letters;

            baby.style.transform = "scale(1.2)";
            setTimeout(() => baby.style.transform = "scale(1)", 300);

            if (data.letters >= 5) {
                portal.classList.remove('hidden');
                baby.style.transform = "scale(0.3) rotate(360deg)";
                baby.style.transition = "1s";

                setTimeout(() => {
                    document.querySelector('.game').style.display = 'none';
                    document.getElementById('world').classList.remove('hidden');
                    setTimeout(enterWorld2, 2000);
                }, 1200);
            }
        })
        .catch(err => console.log('Ошибка fetch:', err));
}

function enterWorld2() {
    document.getElementById('world').classList.add('hidden');
    world2.classList.remove('hidden');

    ['💎', '💎', '💎'].forEach(() => {
        const c = document.createElement('div');
        c.className = 'crystal';
        c.textContent = '💎';
        c.onclick = () => collectCrystal(c);
        crystalsWrap.appendChild(c);
    });
}

function collectCrystal(el) {
    if (el.classList.contains('collected')) return;
    el.classList.add('collected');
    crystalsCollected++;
    crystalCountEl.textContent = crystalsCollected;

    if (crystalsCollected >= 3) {
        portal2.classList.remove('hidden');
    }
}
