"""Dynamic response and fatigue under brushless-motor excitation (extension module).

Excitation: 40,000 RPM = 666.7 Hz fundamental. Simplified models only:
  * Single-degree-of-freedom (SDOF) base-excitation transmissibility of an elastomeric
    damper (Kelvin-Voigt: stiffness k, damping ratio zeta).
  * Natural frequency of a simply supported thin plate / cantilever beam (check for
    resonance separation from the excitation).
  * Basquin S-N fatigue life and Palmgren-Miner cumulative damage.

Placeholders for the team to extend: multi-DOF FE modal analysis, random-vibration PSD,
temperature-dependent elastomer properties, composite fatigue (stiffness degradation).
"""

from __future__ import annotations

import math

import numpy as np


def rpm_to_hz(rpm: float) -> float:
    """Rotation frequency [Hz] from RPM (40,000 RPM -> 666.67 Hz)."""
    return rpm / 60.0


def transmissibility(freq_hz: float, fn_hz: float, zeta: float) -> float:
    """Force/displacement transmissibility of an SDOF isolator.

    T = sqrt(1 + (2 zeta r)^2) / sqrt((1 - r^2)^2 + (2 zeta r)^2),  r = f / fn.
    T < 1 (isolation) only when r > sqrt(2).
    """
    r = freq_hz / fn_hz
    num = 1.0 + (2.0 * zeta * r) ** 2
    den = (1.0 - r**2) ** 2 + (2.0 * zeta * r) ** 2
    return math.sqrt(num / den)


def required_isolator_natural_frequency(freq_hz: float, target_T: float, zeta: float,
                                        r_max: float = 50.0) -> float:
    """Largest isolator natural frequency fn [Hz] achieving T <= target_T at freq_hz.

    Solved by bisection on the frequency ratio r in (sqrt(2), r_max] (T is
    monotonically decreasing there).
    """
    if not 0.0 < target_T < 1.0:
        raise ValueError("target_T must be in (0, 1)")
    lo, hi = math.sqrt(2.0) + 1e-9, r_max
    if transmissibility(freq_hz, freq_hz / hi, zeta) > target_T:
        raise ValueError("target not reachable with given zeta / r_max")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if transmissibility(freq_hz, freq_hz / mid, zeta) > target_T:
            lo = mid
        else:
            hi = mid
    return freq_hz / hi


def isolator_stiffness(mass_kg: float, fn_hz: float) -> float:
    """Total isolator stiffness k = m (2 pi fn)^2 [N/m]."""
    return mass_kg * (2.0 * math.pi * fn_hz) ** 2


def plate_natural_frequency_ss(E_GPa: float, rho_kg_m3: float, t_m: float, a_m: float,
                               b_m: float, nu: float = 0.3) -> float:
    """Fundamental frequency [Hz] of a simply supported isotropic rectangular plate.

    f11 = (pi/2) * sqrt(D / (rho t)) * (1/a^2 + 1/b^2),  D = E t^3 / (12 (1 - nu^2)).
    """
    D = E_GPa * 1e9 * t_m**3 / (12.0 * (1.0 - nu**2))
    return 0.5 * math.pi * math.sqrt(D / (rho_kg_m3 * t_m)) * (1.0 / a_m**2 + 1.0 / b_m**2)


def basquin_cycles(stress_amplitude_MPa: float, sigma_f_prime_MPa: float, b: float) -> float:
    """Cycles to failure N from Basquin: sigma_a = sigma_f' (2N)^b  (b < 0)."""
    if stress_amplitude_MPa <= 0 or b >= 0:
        raise ValueError("stress amplitude must be > 0 and b < 0")
    return 0.5 * (stress_amplitude_MPa / sigma_f_prime_MPa) ** (1.0 / b)


def miner_damage(cycles: np.ndarray | list[float], cycles_to_failure: np.ndarray | list[float]) -> float:
    """Palmgren-Miner damage D = sum(n_i / N_i); failure predicted at D >= 1."""
    n = np.asarray(cycles, dtype=float)
    N = np.asarray(cycles_to_failure, dtype=float)
    return float(np.sum(n / N))


def cycles_in_flight(freq_hz: float, flight_hours: float) -> float:
    """Number of excitation cycles accumulated in a given flight time."""
    return freq_hz * 3600.0 * flight_hours


def stress_cycle(sigma_max_MPa: float, sigma_min_MPa: float) -> dict[str, float]:
    """Parameters of a constant-amplitude stress cycle (tension positive, compression negative).

    Range sigma_i = max - min, amplitude sigma_a = sigma_i / 2, mean sigma_m = (max + min) / 2,
    stress ratio R = min / max. Fully reversed loading has R = -1 and sigma_m = 0.
    """
    if sigma_max_MPa == 0:
        raise ValueError("sigma_max must be non-zero to define R")
    rng = sigma_max_MPa - sigma_min_MPa
    return {"range": rng, "amplitude": rng / 2.0, "mean": (sigma_max_MPa + sigma_min_MPa) / 2.0,
            "R": sigma_min_MPa / sigma_max_MPa}


def hours_for_cycles(cycles: float, freq_hz: float) -> float:
    """Operating hours needed to accumulate ``cycles`` at ``freq_hz`` (inverse of :func:`cycles_in_flight`)."""
    return cycles / (freq_hz * 3600.0)


if __name__ == "__main__":
    f = rpm_to_hz(40_000)
    fn = required_isolator_natural_frequency(f, target_T=0.1, zeta=0.1)
    print(f"Excitation {f:.1f} Hz -> isolator fn <= {fn:.1f} Hz for T = 0.1 (zeta = 0.1)")
    print(f"Cycles per 2 h flight: {cycles_in_flight(f, 2):.3e}")
