(function (root, factory) {
    const api = factory();
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.renderGestureIllustration = api.renderGestureIllustration;
        root.getSupportedGestureIllustrations = api.getSupportedGestureIllustrations;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    const gesturePoses = {
        wave: ['Wave', 'Greeting or farewell', 'open'],
        thumbs_up: ['Thumbs up', 'Positive affirmation', 'thumbs-up'],
        thumbs_down: ['Thumbs down', 'Disagreement or dissatisfaction', 'thumbs-down'],
        peace: ['Peace', 'Peace, victory, or two', 'peace'],
        ok: ['OK', 'Confirmation or approval', 'ok'],
        pointing_up: ['Pointing up', 'Attention or number one', 'pointing'],
        fist: ['Fist', 'Strength, solidarity, or stop', 'fist'],
        open_palm: ['Open palm', 'Stop or wait', 'open'],
        raised_hand: ['Raised hand', 'Question or request for help', 'open'],
        stop: ['Stop', 'Stop or pause', 'open'],
        i_love_you: ['I love you', 'Affection or care', 'love'],
        call_me: ['Call me', 'Contact or casual greeting', 'call'],
        rock_on: ['Rock on', 'Excitement or approval', 'rock'],
        crossed_fingers: ['Crossed fingers', 'Hope or good luck', 'crossed'],
        pinch: ['Pinch', 'Small amount', 'pinch'],
        three: ['Three', 'Number three', 'three'],
        pray: ['Pray', 'Gratitude, request, or respect', 'prayer'],
        clap: ['Clap', 'Applause or appreciation', 'clap'],
    };

    const poses = {
        open: { fingers: [true, true, true, true], thumb: 'open' },
        'thumbs-up': { fingers: [false, false, false, false], thumb: 'up' },
        'thumbs-down': { fingers: [false, false, false, false], thumb: 'down' },
        peace: { fingers: [true, true, false, false], thumb: 'folded' },
        ok: { fingers: [false, true, true, true], thumb: 'pinch' },
        pointing: { fingers: [true, false, false, false], thumb: 'folded' },
        fist: { fingers: [false, false, false, false], thumb: 'folded' },
        love: { fingers: [true, false, false, true], thumb: 'open' },
        call: { fingers: [false, false, false, true], thumb: 'open' },
        rock: { fingers: [true, false, false, true], thumb: 'folded' },
        crossed: { fingers: [true, true, false, false], thumb: 'folded', crossed: true },
        pinch: { fingers: [false, true, false, false], thumb: 'pinch' },
        three: { fingers: [true, true, true, false], thumb: 'folded' },
        prayer: { pair: 'prayer' },
        clap: { pair: 'clap' },
    };

    const fingerX = [36, 52, 68, 84];
    const fingerHeights = [48, 61, 54, 41];
    const handOutline = '#684735';
    const handFill = '#edb78f';

    function renderSingleHand(pose) {
        const fingers = pose.fingers.map((extended, index) => {
            const x = fingerX[index];
            if (extended) {
                const y = 55 - fingerHeights[index];
                return `<rect x="${x}" y="${y}" width="14" height="${fingerHeights[index] + 20}" rx="7" class="gesture-hand-fill"/>`;
            }
            const y = index === 1 ? 46 : 49;
            return `<rect x="${x + 1}" y="${y}" width="12" height="19" rx="6" class="gesture-hand-fill"/>`;
        }).join('');

        const thumb = {
            open: '<path d="M37 78 Q29 74 25 66 L19 57 Q15 52 11 56 Q8 60 12 66 L25 88" class="gesture-hand-fill"/>',
            folded: '<path d="M39 78 Q43 72 49 75 L57 83" class="gesture-hand-fill"/>',
            up: '<path d="M38 81 Q30 72 27 60 L24 45 Q23 38 29 36 Q35 35 38 42 L47 67" class="gesture-hand-fill"/>',
            down: '<path d="M38 82 Q30 88 27 99 L24 112 Q23 119 29 120 Q35 120 38 113 L47 91" class="gesture-hand-fill"/>',
            pinch: '<path d="M38 80 Q30 72 27 63 Q24 56 29 54 Q34 52 38 60 L48 72" class="gesture-hand-fill"/>',
        }[pose.thumb];
        const crossing = pose.crossed
            ? '<path d="M57 47 L80 35 M62 35 L78 48" class="gesture-hand-detail"/>'
            : '';

        return `<g>${fingers}${thumb}
            <path d="M31 57 Q31 51 38 51 H90 Q97 51 97 59 V88 Q97 103 83 109 L80 122 H49 L46 109 Q31 103 31 88 Z" class="gesture-hand-fill"/>
            <path d="M40 60 V67 M56 59 V67 M72 59 V67 M88 60 V67" class="gesture-hand-detail"/>
            ${crossing}
        </g>`;
    }

    function renderGestureIllustration(gestureName, className = '') {
        const definition = gesturePoses[gestureName];
        const pose = definition && poses[definition[2]];
        if (!definition || !pose) {
            return '';
        }

        const handArtwork = pose.pair === 'prayer'
            ? `<g transform="translate(7 37) scale(.53 .72)">${renderSingleHand({ fingers: [true, true, true, true], thumb: 'open' })}</g>
               <g transform="translate(121 37) scale(-.53 .72)">${renderSingleHand({ fingers: [true, true, true, true], thumb: 'open' })}</g>`
            : pose.pair === 'clap'
                ? `<g transform="translate(7 42) scale(.55 .68) rotate(-8 64 80)">${renderSingleHand({ fingers: [true, true, true, true], thumb: 'open' })}</g>
                   <g transform="translate(79 42) scale(.55 .68) rotate(8 64 80)">${renderSingleHand({ fingers: [true, true, true, true], thumb: 'open' })}</g>`
                : renderSingleHand(pose);

        const safeClass = className ? ` ${className.replace(/[^a-zA-Z0-9_-]/g, '')}` : '';
        return `<svg class="gesture-illustration${safeClass}" viewBox="0 0 128 128" role="img" aria-label="${definition[0]} hand illustration" xmlns="http://www.w3.org/2000/svg">
            <style>
                .gesture-hand-fill{fill:${handFill};stroke:${handOutline};stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}
                .gesture-hand-detail{fill:none;stroke:${handOutline};stroke-width:2;stroke-linecap:round}
            </style>
            ${handArtwork}
        </svg>`;
    }

    function getSupportedGestureIllustrations() {
        return Object.entries(gesturePoses).map(([gesture, [label, meaning]]) => ({
            gesture,
            label,
            meaning,
        }));
    }

    return { renderGestureIllustration, getSupportedGestureIllustrations };
}));
