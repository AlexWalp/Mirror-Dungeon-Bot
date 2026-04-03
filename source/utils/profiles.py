import random
import threading

import source.utils.params as p


_PROFILE_DEFAULT = "SAFE"

PROFILES = {
    "SAFE": {
        "mouse_velocity": 0.58,
        "noise": 3.2,
        "endpoint_jitter_px": 8,
        "delay_jitter": (0.65, 1.5),
        "step_sleep_jitter": (0.7, 1.4),
        "click_interval_jitter": (0.6, 1.7),
        "key_interval_jitter": (0.7, 1.4),
        "final_delay_human": (0.03, 0.12),
        "final_delay_nonhuman": (0.025, 0.05),
        "rhythm_every_actions": (5, 25),
        "rhythm_pause": (0.1, 1.2),
        "neutral_drift_px": 6,
        "neutral_drift_chance": 0.45,
        "mouse_velocity_jitter": (0.7, 1.4),
        "noise_jitter": (0.6, 1.5),
        "long_pause_chance": 0.04,
        "long_pause_range": (1.0, 3.5),
    },
    "FAST": {
        "mouse_velocity": 0.78,
        "noise": 2.0,
        "endpoint_jitter_px": 6,
        "delay_jitter": (0.7, 1.35),
        "step_sleep_jitter": (0.75, 1.3),
        "click_interval_jitter": (0.7, 1.5),
        "key_interval_jitter": (0.75, 1.3),
        "final_delay_human": (0.02, 0.07),
        "final_delay_nonhuman": (0.022, 0.04),
        "rhythm_every_actions": (8, 22),
        "rhythm_pause": (0.06, 0.8),
        "neutral_drift_px": 4,
        "neutral_drift_chance": 0.35,
        "mouse_velocity_jitter": (0.8, 1.3),
        "noise_jitter": (0.7, 1.4),
        "long_pause_chance": 0.02,
        "long_pause_range": (0.5, 2.0),
    },
    "CHAOTIC": {
        "mouse_velocity": 0.5,
        "noise": 4.2,
        "endpoint_jitter_px": 12,
        "delay_jitter": (0.5, 1.8),
        "step_sleep_jitter": (0.55, 1.6),
        "click_interval_jitter": (0.5, 2.0),
        "key_interval_jitter": (0.55, 1.7),
        "final_delay_human": (0.02, 0.15),
        "final_delay_nonhuman": (0.02, 0.06),
        "rhythm_every_actions": (3, 20),
        "rhythm_pause": (0.1, 2.0),
        "neutral_drift_px": 10,
        "neutral_drift_chance": 0.6,
        "mouse_velocity_jitter": (0.5, 1.6),
        "noise_jitter": (0.4, 1.8),
        "long_pause_chance": 0.06,
        "long_pause_range": (1.5, 5.0),
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

    # Occasional long pause to simulate human distraction
    long_chance = profile.get("long_pause_chance", 0.03)
    long_range = profile.get("long_pause_range", (1.0, 3.0))
    if random.random() < long_chance:
        pause += random.uniform(*long_range)

    drift = (0, 0)
    if random.random() < profile["neutral_drift_chance"]:
        max_drift = profile["neutral_drift_px"]
        drift = (
            random.randint(-max_drift, max_drift),
            random.randint(-max_drift, max_drift),
        )

    return pause, drift
