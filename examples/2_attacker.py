
import asyncio
import sys
import os
# Add project root to path
sys.path.append(os.getcwd())

from src.bsg.chargepoint.simulator import ChargePointSimulator
from src.bsg.utils.logging import setup_logger

logger = setup_logger("Attacker")

async def simulate_attacker():
    csms_url = "ws://localhost:9000"
    cp_id = "CP_PHANTOM_X"
    reservation_id = "RES_12345" # SAME RESERVATION ID!
    
    logger.info(f"--- Starting ATTACK Simulation ---")
    logger.info(f"Target CSMS: {csms_url}")
    logger.info(f"Stolen Reservation ID: {reservation_id}")
    
    cp = ChargePointSimulator(cp_id, csms_url)
    
    try:
        await cp.start()
        await asyncio.sleep(1)
        
        # Attempt Duplicate Booking
        logger.info("😈 Attempting to hijack session (Duplicate Booking)...")
        response = await cp.send_start_transaction(
            reservation_id=reservation_id,
            id_tag="ATTACKER_TAG",
            connector_id=1
        )
        
        status = response['status']
        logger.info(f"Attack Transaction Status: {status}")
        
        if status == "Accepted":
            logger.warning("⚠️  VULNERABILITY SUCCESSFUL! The system accepted the duplicate booking.")
            logger.warning("   The attacker is now charging on the victim's reservation.")
        else:
            logger.info("🛡️  ATTACK BLOCKED! The system rejected the duplicate booking.")
            logger.info("   The security mechanism is working correctly.")
            
    except OSError:
        logger.error("Could not connect to CSMS. is the server running?")
    finally:
        await cp.stop()

if __name__ == "__main__":
    asyncio.run(simulate_attacker())
