
import asyncio
import sys
import os
# Add project root to path to import src
sys.path.append(os.getcwd())

from src.bsg.chargepoint.simulator import ChargePointSimulator
from src.bsg.utils.logging import setup_logger

logger = setup_logger("LegitUser")

async def simulate_legit_user():
    csms_url = "ws://localhost:9000"
    cp_id = "CP_LEGIT_001"
    reservation_id = "RES_12345"
    
    logger.info(f"--- Starting Legitimate Session ---")
    logger.info(f"Target CSMS: {csms_url}")
    logger.info(f"Reservation ID: {reservation_id}")
    
    cp = ChargePointSimulator(cp_id, csms_url)
    
    try:
        await cp.start()
        await asyncio.sleep(1)
        
        # Start Transaction
        logger.info("Initiating StartTransaction...")
        response = await cp.send_start_transaction(
            reservation_id=reservation_id,
            id_tag="USER_LEGIT",
            connector_id=1
        )
        
        status = response['status']
        logger.info(f"Transaction Status: {status}")
        
        if status == "Accepted":
            logger.info("✅ Charging session started successfully.")
            logger.info("🔌 Charging in progress... (Press Ctrl+C to stop)")
            
            # Simulate charging duration (keep session active)
            while True:
                await asyncio.sleep(5)
                logger.info("... Charging ...")
        else:
            logger.error(f"❌ Failed to start transaction. Status: {status}")
            
    except OSError:
        logger.error("Could not connect to CSMS. is the server running?")
    except KeyboardInterrupt:
        logger.info("Stopping session...")
    finally:
        await cp.stop()

if __name__ == "__main__":
    try:
        asyncio.run(simulate_legit_user())
    except KeyboardInterrupt:
        pass
