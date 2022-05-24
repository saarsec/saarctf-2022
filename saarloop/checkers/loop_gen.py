# note affinities in a minor scale
import copy
import json
import logging
import math
import os
import random
import subprocess
import sys

CHORD_MATRIX = [
    # C Db  D Eb  E  F Gb  G Ab  A Bb  B
    [9, 0, 2, 5, 0, 1, 0, 7, 0, 0, 3, 0],  # C
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Db
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # D
    [2, 0, 3, 9, 0, 2, 0, 5, 0, 0, 7, 0],  # Eb
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # E
    [7, 0, 0, 3, 0, 9, 0, 2, 5, 0, 1, 0],  # F
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Gb
    [2, 0, 7, 1, 0, 3, 0, 9, 0, 0, 5, 0],  # G
    [5, 0, 0, 7, 0, 2, 0, 3, 9, 0, 3, 0],  # Ab
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # A
    [2, 0, 5, 2, 0, 7, 0, 2, 0, 0, 9, 0],  # Bb
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # B
]

# alternative major root chord
#                   C Db  D Eb  E  F Gb  G Ab  A Bb  B
ROOT_ALTERNATIVE = [9, 0, 2, 0, 5, 0, 0, 7, 0, 1, 0, 3]  # C

CHORD_ROOTS = [i for i, c in enumerate(CHORD_MATRIX) if sum(c)]

NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

VOL_NORMALIZATION = {
    'fat_saw': 0.4,
    'saw': 0.2,
    'square': 0.2,
    'sine': 1.0
}

BASS_SYNTHS = ["fat_saw", "saw", "square", "sine"]
CHORD_SYNTHS = ["fat_saw", "saw", "square", "sine"]

DRUM_SAMPLES = {
    "KICK": ["KICK_comb-5", "KICK_comb-6-deeecent", "KICK_decent", "KICK_hybrid-1", "KICK_layered", "KICK_punchy-1",
             "KICK_punchy-2", "KICK_punchy-3", "KICK_punchy4-10-1", "KICK_punchy-5-9", "KICK_soft"],
    "SNARE": ["SNARE_11", "SNARE_26", "SNARE_27", "SNARE_ac-mix-1", "SNARE_clap", "SNARE_combine-1",
              "SNARE_combined-12", "SNARE_combined-13", "SNARE_combined-15", "SNARE_combined-16-punchy",
              "SNARE_combined-17-roomy", "SNARE_combined-6", "SNARE_combined-7", "SNARE_combined-9", "SNARE_driven",
              "SNARE_dual-27-11", "SNARE_edm-style", "SNARE_hybrid-1-rezzy", "SNARE_hybrid-1", "SNARE_hybrid-2",
              "SNARE_hybrid-3", "SNARE_hybrid-4", "SNARE_hybrid-5", "SNARE_low-hit", "SNARE_not-great",
              "SNARE_pitched-19102013", "SNARE_spyre-power", "SNARE_synth-transient"],
    "HIHAT_CLOSED": ["HI-HAT_closed-10", "HI-HAT_closed-1", "HI-HAT_closed-2", "HI-HAT_closed-3", "HI-HAT_closed-4",
                     "HI-HAT_closed-5", "HI-HAT_closed-6", "HI-HAT_closed-7", "HI-HAT_closed-8", "HI-HAT_closed-9"],
    "HIHAT_OPEN": ["HI-HAT_open-1", "HI-HAT_open-2"]

}
# ptn_length, ptn
# instrument, vol, notes
GROOVES = [
    (1, [("KICK", 1, [0, 1, 2, 3]),
         ("SNARE", 1, [1, 3]),
         ("HIHAT_CLOSED", 1, [0.5, 1.5, 2.5, 3.5])]),
    (2, [("KICK", 1, [0, 1, 2, 3, 4, 5, 6, 7]),
         ("SNARE", 1, [1, 3, 5, 7]),
         ("SNARE|1", 0.75, [7.75]),
         ("HIHAT_CLOSED", 1, [0.5, 1.5, 2.5, 3.5])]),
    (2, [("KICK", 1, [0, 4, 5]),
         ("SNARE", 1, [2, 6]),
         ("HIHAT_CLOSED", 1, [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])]),
    (4, [("KICK", 1, [0, 2.75, 4, 6.75, 8, 10.5, 12.75, 14.5]),
         ("KICK", 0.6, [0.5, 2.5, 4.5, 6.5, 8.5, 12.5]),
         ("SNARE", 1, [1, 3, 5, 7, 9, 11.5, 13, 15.5]),
         ("SNARE", 0.6, [1.75, 2.25, 3.75, 5.75, 6.25, 7.75, 9.75, 10.25, 12.25, 13.75, 14.25]),
         ("HIHAT_CLOSED", 1,
          [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5,
           13, 13.5, 14, 15, 15.5]),
         ("HIHAT_OPEN", 1, [14.5])])
]


def normalize(vec):
    if isinstance(vec, list):
        s = sum(vec)
        return [v / s for v in vec]
    elif isinstance(vec, dict):
        s = sum(vec.values())
        return {k: v / s for k, v in vec.items()}
    else:
        raise ValueError(f"cannot normalize value of type {type(vec)}")


def gen_root_loop(n=4):
    return [0] + random.choices(CHORD_ROOTS, k=n - 1)


def pick_chord(bass_note, n_voices=None):
    chord = CHORD_MATRIX[bass_note]
    if bass_note == 0 and random.random() < 0.05:
        # with a tiny probability make the first chord a major chord
        chord = ROOT_ALTERNATIVE
    n_voices = n_voices or random.choice([2, 3, 3, 4, 4, 4, 5, 5])
    logging.debug(f"Attempting to find a chord sequence with {n_voices} voices")
    chord_weights = {i: w for i, w in enumerate(chord) if w > 0}
    chord_notes = set()
    while len(chord_notes) < n_voices:
        new_note = random.choices(*zip(*chord_weights.items()))[0]
        del chord_weights[new_note]
        chord_notes.add(new_note)

    return sorted(chord_notes)


def random_inversion(chord_notes):
    n_voices = len(chord_notes)
    shift_notes = random.randint(0, n_voices)
    for i in range(shift_notes):
        chord_notes[i] += 12
    # if we've shifted more than half of the chord move everything down an octave
    # so the "center" remains within the same octave
    if shift_notes > n_voices / 2:
        for i in range(n_voices):
            chord_notes[i] -= 12
    return chord_notes


def print_mat(voice):
    logging.debug(' '.join(n.rjust(5) for n in NOTE_NAMES))
    for step in voice:
        if step.is_fixed:
            logging.debug(f'FIXED: {NOTE_NAMES[step.val % 12]}')
        else:
            single_octave_view = [0] * 12
            for k, v in step.items():
                single_octave_view[k % 12] = v
            logging.debug(' '.join(f'{x:5.2f}' for x in single_octave_view))

    logging.debug('')


class Possibility(dict):
    """
    Maps values to their probability (although we ignore normalization for now...)
    confusing in python-lingo, because our *values* become dict-*keys*,
    while the dict-*values* correspond to the probabilities
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._exclusions = set()
        self._initialized = len(self) > 0

    @property
    def is_fixed(self):
        return len(self) == 1

    @property
    def val(self):
        if not self.is_fixed:
            raise ValueError("Not fixed yet")
        else:
            return next(iter(self.keys()))

    @property
    def is_initialized(self):
        return self._initialized

    def __setitem__(self, key, value):
        if value == 0:
            del self[key]
        elif key not in self._exclusions:
            super().__setitem__(key, value)
            self._initialized = True

    def __delitem__(self, key):
        self._exclusions.add(key)
        if key in self:
            super().__delitem__(key)

    def set(self, key):
        for k in set(self.keys()):
            if k != key:
                del self[k]
        if key not in self:
            self[key] = 1.0

    def normalize(self):
        vs = sum(self.values())
        for k in self.keys():
            self[k] /= vs


class WaveFunctionCollapse:
    def __init__(self, bass_notes, n_voices):
        self.bass_notes = bass_notes
        self.n_voices = n_voices
        self.possibilities = [[Possibility() for _ in range(self.n_steps)] for _ in range(self.n_voices)]

    @property
    def n_steps(self):
        return len(self.bass_notes)

    def eliminate_value(self, voice, step, choice):
        if self.possibilities[voice][step].is_fixed:  # is this step already fixed? check for collisions
            if self.possibilities[voice][step].val != choice:  # different value? -> all good
                return
            else:
                raise ValueError()  # same value? -> trouble
        else:  # not fixed yet? eliminate possibility
            if choice not in self.possibilities[voice][step]:  # was already impossible? -> all good
                return
            del self.possibilities[voice][step][choice]
            if self.possibilities[voice][step].is_initialized:
                self.check_options_and_propagate(voice, step)

    def check_options_and_propagate(self, voice, step):
        options = self.possibilities[voice][step]
        if not options:  # no options left? -> trouble
            raise ValueError()
        if options.is_fixed:  # only one option left? -> fix it
            self.fix_value(voice, step, options.val)
        else:  # otherwise: normalize and propagate
            self.possibilities[voice][step].normalize()
            self.check_compatibility(voice, step, step - 1)
            self.check_compatibility(voice, step, step + 1)

    def check_compatibility(self, voice, changed_step, step):
        changed_step %= self.n_steps
        step %= self.n_steps
        if self.possibilities[voice][changed_step].is_fixed:
            # a value was just fixed -> apply boosts if current step is not fixed yet
            fixed_note = self.possibilities[voice][changed_step].val
            if self.possibilities[voice][step].is_fixed:
                if abs(self.possibilities[voice][step].val - fixed_note) > 3:  # outside of range? -> trouble
                    raise ValueError()
                else:  # within permissible range? -> all good
                    return
            elif not self.possibilities[voice][step].is_initialized:
                for d in range(-3, 4):
                    self.possibilities[voice][step][fixed_note + d] = CHORD_MATRIX[self.bass_notes[step]][
                        (fixed_note + d) % 12]
                self.check_options_and_propagate(voice, step)
            else:  # undecided here? -> apply boosts
                key_set = sorted(self.possibilities[voice][step].keys())
                for i in key_set:
                    if abs(i - fixed_note) > 3:
                        del self.possibilities[voice][step][i]  # outside of range? -> remove
                    else:
                        self.possibilities[voice][step][i] *= 1 + 0.5 ** abs(i - fixed_note)  # in range? -> boost
                self.check_options_and_propagate(voice, step)
        else:
            if self.possibilities[voice][step].is_fixed:  # already fixed here? assume everything is in order
                return
            elif not self.possibilities[voice][step].is_initialized:
                possible_notes = set(
                    k + d for k in self.possibilities[voice][changed_step].keys() for d in range(-3, 4))
                for n in possible_notes:
                    self.possibilities[voice][step][n] = CHORD_MATRIX[self.bass_notes[step]][n % 12]
                self.check_options_and_propagate(voice, step)
            else:
                changed = False
                key_set = sorted(self.possibilities[voice][step].keys())
                for i in key_set:
                    if sum(self.possibilities[voice][changed_step].get((i + d) % 12, 0) for d in range(-3, 4)) > 0:
                        # is there an option within permissible range? -> no change needed
                        continue
                    else:
                        del self.possibilities[voice][step][i]
                        changed = True
                if changed:
                    self.check_options_and_propagate(voice, step)

    def fix_value(self, voice, step, choice):
        if self.possibilities[voice][step].is_fixed:  # is this step already fixed? check for collisions
            if self.possibilities[voice][step].val == choice:  # same value? -> all good
                return
            else:
                raise ValueError()  # different value? -> trouble
        else:  # not fixed yet? fix and propagate
            self.possibilities[voice][step].set(choice)
            self.check_compatibility(voice, step, step - 1)
            self.check_compatibility(voice, step, step + 1)
            for v, _ in enumerate(self.possibilities):
                if v != voice:
                    self.eliminate_value(v, step, choice)

    def resolve(self):
        logging.debug('=' * 16 + ' STATE ' + '=' * 16)
        for voice in self.possibilities:
            print_mat(voice)

        unresolved = [(voice, step) for voice, voice_v in enumerate(self.possibilities) for step, step_v in
                      enumerate(voice_v) if
                      not step_v.is_fixed and step_v.is_initialized]

        while unresolved:
            voice, step = random.choice(unresolved)
            keys, weights = zip(*self.possibilities[voice][step].items())
            note = random.choices(keys, weights, k=1)[0]
            logging.debug(f"Fixing {voice=} {step=} to {note=}")
            self.fix_value(voice, step, note)

            logging.debug('=' * 16 + ' STATE ' + '=' * 16)
            for voice in self.possibilities:
                print_mat(voice)

            unresolved = [(voice, step) for voice, voice_v in enumerate(self.possibilities) for step, step_v in
                          enumerate(voice_v) if
                          not step_v.is_fixed and step_v.is_initialized]

        logging.debug('=' * 16 + ' STATE ' + '=' * 16)
        for voice in self.possibilities:
            print_mat(voice)

    def get_chords(self):
        return [[v.val for v in voices] for voices in zip(*self.possibilities)]


def gen_chord_sequence(bass_notes, initial_chord=None):
    initial_chord = initial_chord or random_inversion(pick_chord(bass_notes[0]))

    n_voices = len(initial_chord)

    wf = WaveFunctionCollapse(bass_notes, n_voices)

    for voice, note in enumerate(initial_chord):
        wf.fix_value(voice, 0, note)

    wf.resolve()

    chords = wf.get_chords()

    return chords


def transpose(steps):
    t = random.randint(0, 11)
    return [(b + t, [c + t for c in chord]) for b, chord in steps]


def assign_notes(steps):
    bass_root_C = 24  # + random.randint(0, 1) * 12
    chords_root_C = 60  # + random.randint(-1, 1) * 12
    return [(b + bass_root_C, [c + chords_root_C for c in chord]) for b, chord in steps]


def assign_timing(steps):
    timed_steps = [[4 * t, step] for t, step in enumerate(steps)]
    r = random.random()

    if r > 0.8:  # with 20% probability take the last chord early
        pull = random.choice([0.25, 0.5, 1, 2])
        timed_steps[-1][0] -= pull
        if r > 0.95 and len(timed_steps) >= 4:  # with 5% also take the midway chord early
            timed_steps[len(timed_steps) // 2][0] -= pull

    return timed_steps


def is_valid_duration(inc, bpm):
    return (60 / bpm) * inc * 11025 <= 16384


def render_bass(bass_steps, energy, bpm):
    bass_tone = random.choice(BASS_SYNTHS)
    track = {
        "type": "SYNTH_PRESET",
        "id": bass_tone,
        "vol": min(0.4, max(0.2, (energy + (random.random() - 0.5) * 0.4))) * VOL_NORMALIZATION[bass_tone] * 0.75,
        "env": {
            "a": 256,
            "d": 256 + (1 - energy) * 8192,
            "s": 0.5 + energy * 0.5,
            "r": 256
        }
    }

    notes = []
    t = 0.5
    iter_steps = zip(bass_steps, bass_steps[1:] + [None])
    cur_step, next_step = next(iter_steps)
    inc = [2, 1, 0.5, 0.25][int(energy * 4)]

    while not is_valid_duration(inc, bpm):
        inc /= 2

    while t < len(bass_steps) * 4:
        while next_step and t > next_step[0]:
            cur_step, next_step = next(iter_steps)
        if math.fmod(t, 1) >= 0.25:
            notes.append({"t": t, "p": cur_step[1], "d": inc})
            if bass_tone == "sine":
                # octave-boost sine waves
                notes.append({"t": t, "p": cur_step[1] + 12, "d": inc})
        t += inc

    track['notes'] = notes
    return track


def render_delay(orig_track, delay, amp, length):
    track = copy.deepcopy(orig_track)
    track['vol'] *= amp
    for n in track['notes']:
        n['t'] += delay
        n['t'] %= length
    return track


def render_chords(chord_steps, energy, bpm):
    chord_synth = random.choice(CHORD_SYNTHS)
    track = {
        "type": "SYNTH_PRESET",
        "id": chord_synth,
        "vol": min(0.25, max(0.1, (energy + (random.random() - 0.5) * 0.25))) * VOL_NORMALIZATION[chord_synth],
        "env": {
            "a": 256,
            "d": 2048 + (1 - energy) * 8192,
            "s": 0.05,
            "r": 256
        }
    }

    notes = []
    t = 0

    n_voices = len(chord_steps[1][1])
    iter_steps = zip(chord_steps, chord_steps[1:] + [None])
    cur_step, next_step = next(iter_steps)
    # inc = [2, 1.5, 1, 0.75, 0.5][int(energy * 5)]
    # logging.debug(f"{inc=} {energy=}")

    delay = False

    if random.random() < 0.5 and n_voices > 2:
        # arp-mode
        delay = random.random() < 0.75
        inc = [1.5, 1, 0.5][int(energy * 3)]
        while not is_valid_duration(inc * 1.5, bpm):
            inc /= 2
        i = 0
        while t < len(chord_steps) * 4:
            while next_step and t >= next_step[0]:
                cur_step, next_step = next(iter_steps)
            i %= len(2 * cur_step[1])
            if i >= len(cur_step[1]):
                shift = 12
            else:
                shift = 0
            notes.append({"t": t, "p": shift + cur_step[1][i % len(cur_step[1])], "d": inc * 1.5})
            t += inc
            i += 1
    else:
        # chord mode
        inc = [2, 1.5, 1, 0.75][int(energy * 4)]
        while not is_valid_duration(inc * 1.5, bpm):
            inc /= 2
        while t < len(chord_steps) * 4:
            while next_step and t >= next_step[0]:
                cur_step, next_step = next(iter_steps)
            for p in cur_step[1]:
                notes.append({"t": t, "p": p, "d": inc * 1.5})
            t += inc
        track['vol'] *= 0.5

    track['notes'] = notes

    tracks = [track]
    if delay:
        tracks.append(
            render_delay(track, inc * random.choice([1.5, 1.5, 1.5, 2.5, 2.5, 3.5]), 0.5, len(chord_steps) * 4))
        for t in tracks:
            t['vol'] *= 0.6

    return tracks


def render_drums(length, energy):
    bars, groove = random.choice(GROOVES)

    samples = {}

    tracks = []
    for instrument, vol, notes in groove:
        if instrument not in samples:
            sample = random.choice(DRUM_SAMPLES[instrument.split("|", maxsplit=1)[0]])
            samples[instrument] = sample
        else:
            sample = samples[instrument]
        tracks.append(
            {"type": "SAMPLE_PRESET",
             "id": sample,
             "vol": min(0.5, max(0.3, (energy + (random.random() - 0.5) * 0.6))) * vol,
             "notes": [n + 4 * x for x in range(0, length, bars) for n in notes]
             })
    return tracks


def render_loop(timed_note_steps):
    energy = random.random()
    bpm = random.randint(90, 150)

    tracks = []

    bass = render_bass([(t, b) for (t, (b, chord)) in timed_note_steps], energy, bpm)
    tracks.append(bass)

    chord_tracks = render_chords([(t, chord) for (t, (b, chord)) in timed_note_steps], energy, bpm)
    tracks.extend(chord_tracks)

    tracks.extend(render_drums(len(timed_note_steps), energy))

    loop = {
        "bpm": bpm,
        "length": 4 * len(timed_note_steps),
        "tracks": tracks
    }
    return loop


def gen_loop():
    loop_len = random.choice([4, 8])
    bass_notes = gen_root_loop(n=loop_len)
    while True:
        try:
            chords = gen_chord_sequence(bass_notes)
            break
        except ValueError:
            logging.debug("Retrying...")
            pass

    steps = zip(bass_notes, chords)

    steps = transpose(steps)

    # logging.debug(f"Loop:")
    # for b, chord in steps:
    # logging.debug(f"- {NOTE_NAMES[b % 12]}:\t{', '.join(NOTE_NAMES[c % 12] for c in chord)}")

    note_steps = assign_notes(steps)

    timed_note_steps = assign_timing(note_steps)

    return render_loop(timed_note_steps)


def main():
    loop = gen_loop()
    loop_num = 0
    while os.path.exists(f'./test/loop_{loop_num:03}.json'):
        loop_num += 1

    with open(f'./test/loop_{loop_num:03}.json', 'w') as f:
        json.dump(loop, f)
    # logging.debug(json.dumps(loop))
    with open(f'./test/loop_{loop_num:03}.wav', 'wb') as out_f:
        p = subprocess.run(["../service/engine/saarloop_engine", "user"], input=json.dumps(loop).encode(), stdout=out_f,
                           stderr=sys.stderr, cwd="../service/")

    # logging.debug(p.returncode)


if __name__ == '__main__':
    main()
