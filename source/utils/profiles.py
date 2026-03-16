import random
import threading

import source.utils.params as p


_PROFILE_DEFAULT = "SAFE"

PROFILES = {
    "SAFE": {
        "mouse_velocity": 0.58,
        "noise": 3.2,
        "endpoint_jitter_px": 3,
        "delay_jitter": (0.9, 1.1),
        "step_sleep_jitter": (0.9, 1.15),
        "click_interval_jitter": (0.9, 1.2),
        "key_interval_jitter": (0.9, 1.15),
        "final_delay_human": (0.03, 0.07),
        "final_delay_nonhuman": (0.028, 0.034),
        "rhythm_every_actions": (7, 12),
        "rhythm_pause": (0.06, 0.2),
        "neutral_drift_px": 3,
        "neutral_drift_chance": 0.35,
    },
    "FAST": {
        "mouse_velocity": 0.78,
        "noise": 2.0,
        "endpoint_jitter_px": 4,
        "delay_jitter": (0.92, 1.08),
        "step_sleep_jitter": (0.9, 1.1),
        "click_interval_jitter": (0.92, 1.12),
        "key_interval_jitter": (0.92, 1.1),
        "final_delay_human": (0.02, 0.045),
        "final_delay_nonhuman": (0.025, 0.032),
        "rhythm_every_actions": (10, 16),
        "rhythm_pause": (0.04, 0.12),
        "neutral_drift_px": 2,
        "neutral_drift_chance": 0.25,
    },
    "CHAOTIC": {
        "mouse_velocity": 0.5,
        "noise": 4.2,
        "endpoint_jitter_px": 5,
        "delay_jitter": (0.82, 1.25),
        "step_sleep_jitter": (0.8, 1.25),
        "click_interval_jitter": (0.82, 1.3),
        "key_interval_jitter": (0.85, 1.22),
        "final_delay_human": (0.025, 0.09),
        "final_delay_nonhuman": (0.026, 0.04),
        "rhythm_every_actions": (5, 10),
        "rhythm_pause": (0.08, 0.3),
        "neutral_drift_px": 5,
        "neutral_drift_chance": 0.5,
    },
}


_rhythm_lock = threading.Lock()
_rhythm_counter = 0
_rhythm_next = random.randint(*PROFILES[_PROFILE_DEFAULT]["rhythm_every_actions"])


def _normalize_profile_name(profile_name=None):
    selected = profile_name if profile_name is not None else getattr(p, "MACRO_PROFILE", _PROFILE_DEFAULT)
    selected = str(selected).upper()
    if selected not in PROFILES:
        return _PROFILE_DEFAULT
    return selected


def get_macro_profile(profile_name=None):
    return PROFILES[_normalize_profile_name(profile_name)]


def randomize_with_profile(base_value, profile=None, key="delay_jitter"):
    if base_value <= 0:
        return base_value
    profile = profile or get_macro_profile()
    jitter_min, jitter_max = profile[key]
    return base_value * random.uniform(jitter_min, jitter_max)


def maybe_rhythm_jitter(profile=None):
    if not getattr(p, "MACRO_RHYTHM", True):
        return 0.0, (0, 0)

    profile = profile or get_macro_profile()
    every_min, every_max = profile["rhythm_every_actions"]

    global _rhythm_counter, _rhythm_next

    with _rhythm_lock:
        _rhythm_counter += 1
        if _rhythm_counter < _rhythm_next:
            return 0.0, (0, 0)

        _rhythm_counter = 0
        _rhythm_next = random.randint(every_min, every_max)

    pause_min, pause_max = profile["rhythm_pause"]
    pause = random.uniform(pause_min, pause_max)

    drift = (0, 0)
    if random.random() < profile["neutral_drift_chance"]:
        max_drift = profile["neutral_drift_px"]
        drift = (
            random.randint(-max_drift, max_drift),
            random.randint(-max_drift, max_drift),
        )

    return pause, drift
