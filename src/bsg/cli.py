
import asyncio
import argparse
import sys
import logging
from src.bsg.csms.server import CSMSimulator
from src.bsg.utils.logging import setup_logger

logger = setup_logger("BSG_CLI")

async def run_server(port: int, secure: bool):
    """Runs the CSMS server indefinitely."""
    server = CSMSimulator(port=port, secure_mode=secure)
    await server.start()
    
    # Keep the server running until interrupted
    try:
        await asyncio.Future()  # run forever
    except asyncio.CancelledError:
        pass
    finally:
        await server.stop()

def main():
    parser = argparse.ArgumentParser(description="BSG OCPP Security Simulator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the CSMS Server")
    server_parser.add_argument("--port", type=int, default=9000, help="Port to listen on (default: 9000)")
    server_parser.add_argument("--secure", action="store_true", help="Enable secure mode (prevention)")
    server_parser.add_argument("--vulnerable", action="store_false", dest="secure", help="Enable vulnerable mode (default)")
    server_parser.set_defaults(secure=False)

    args = parser.parse_args()
    
    if args.command == "server":
        try:
            asyncio.run(run_server(args.port, args.secure))
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
