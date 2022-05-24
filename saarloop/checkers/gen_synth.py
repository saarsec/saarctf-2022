#!/usr/bin/env python3
# coding: utf-8

import math
import json
import scipy.fft

# corresponds to a 175Hz tone at 11025Hz sample freq (roughly an F)
# to "reconstruct", play this synth at MIDI-note 41
SAMPLE_LEN = 63

def get_coeffs(target):
    """
    return dct coefficients for easy "backwards" use with plain cosine functions
    """
    return scipy.fft.dct(to_float(target), type=3, norm="forward")


def to_float(data):
    return [2 * x / 255.0 - 1.0 for x in data]

def to_bytes(data):
    return bytes(int(round(255 * (x + 1.0) / 2.0)) for x in data)


def bytes_to_synth(flag):
    # all flag/ascii bytes are <127 and thus <0.0
    # to generate a "smooth" sound (and hopefully few resampling artifacts)
    # we can pad it out with a partial sine-quarterwave
    # as the inverse DCT will complement the three other quarters like this:
    # 0. original
    # 1. reversed + flipped
    # 2. flipped
    # 3. reversed

    # compute min value of the flag bytes
    # = amplitude of the sample
    flag_min = min(flag)
    amp = 2 * flag_min / 255.0 - 1.0

    # pad flag with quarter sinewave (actually, use a quarter cosine wave)
    pad_len = SAMPLE_LEN - len(flag)
    padded_flag_bytes = flag + to_bytes(
        amp * math.cos(i / pad_len * math.pi / 2) for i in range(pad_len)
    )
    coeffs = get_coeffs(padded_flag_bytes)
    import json
    oscs = [
        {"type": "SINE", "vol": 2 * c, "phase": math.pi / 2, "fmult": (i + 1 / 2)}
        for i, c in enumerate(coeffs)
    ]
    return {"oscs": oscs}



def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    args = parser.parse_args()
    print(json.dumps(bytes_to_synth(args.text.encode())))

if __name__ == '__main__':
    main()
