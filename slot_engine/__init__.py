"""A minimal, interview-grade slot game engine + Monte Carlo simulation bot.

Modules:
    machine  - SlotMachine, ReelStrip, Paytable, SpinResult
    bot      - SimulationBot, RunningStats (Welford online mean/variance)
    simulate - runnable demo: builds a machine and runs a simulation
    parallel - multiprocessing runner that uses all CPU cores
"""
from .machine import SlotMachine, ReelStrip, Paytable, SpinResult
from .bot import SimulationBot, RunningStats

__all__ = [
    "SlotMachine", "ReelStrip", "Paytable", "SpinResult",
    "SimulationBot", "RunningStats",
]
