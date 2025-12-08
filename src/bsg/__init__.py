"""
BSG - OCPP Security Simulator Package
=====================================

A professional OCPP 1.6 simulator for testing EV charging station security.

Modules:
    - chargepoint: ChargePoint simulator for connecting to CSMS
    - csms: Central System Management Server simulator
    - utils: Logging and helper utilities
    - cli: Command-line interface

Usage:
    # Start CSMS server (vulnerable mode)
    python -m src.bsg.cli server --port 9000 --vulnerable
    
    # Start CSMS server (secure mode)
    python -m src.bsg.cli server --port 9000 --secure
"""

__version__ = "1.0.0"
__author__ = "EV Charging Security Research Team"

