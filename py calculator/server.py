import sys
import Ice
import traceback
import json
import logging
import time
import os

# Load Ice slice files
SLICE_PATH = os.path.join(os.path.dirname(__file__), 'calculator.ice')
Ice.loadSlice('', ['-I' + Ice.getSliceDir(), SLICE_PATH])
import Calculator
from calculator import calculator_impl

class CalculatorApp(Ice.Application):
    def __init__(self):
        super().__init__()
        self.adapter = None
        self.servant = None
        self.is_running = False

    def run(self, args):
        try:
            # Load configuration
            with open('config.json', 'r') as f:
                config = json.load(f)

            # Configure logging
            logging.basicConfig(
                level=config['logging']['level'],
                format=config['logging']['format']
            )

            print("Starting Calculator Server...")
            broker = self.communicator()
            
            # Create adapter
            self.adapter = broker.createObjectAdapterWithEndpoints(
                config['ice']['adapter_name'],
                config['ice']['endpoint']
            )
            
            # Create and add servant
            self.servant = calculator_impl.CalculatorI()
            self.adapter.add(
                self.servant,
                broker.stringToIdentity(config['ice']['identity'])
            )
            
            # Activate adapter
            self.adapter.activate()
            self.is_running = True
            
            print(f"Calculator Server is ready and listening on {config['ice']['endpoint']}!")
            print("Press Ctrl+C to stop the server")
            
            self.shutdownOnInterrupt()
            broker.waitForShutdown()
            return 0

        except Ice.Exception as e:
            logging.error(f"Ice error starting server: {str(e)}")
            logging.error(traceback.format_exc())
            return 1
        except Exception as e:
            logging.error(f"Error starting server: {str(e)}")
            logging.error(traceback.format_exc())
            return 1
        finally:
            self.cleanup()

    def cleanup(self):
        if self.is_running:
            logging.info("Shutting down server...")
            try:
                if self.adapter:
                    self.adapter.deactivate()
                if self.servant:
                    self.servant = None
                self.is_running = False
                logging.info("Server shutdown complete")
            except Exception as e:
                logging.error(f"Error during shutdown: {str(e)}")
                logging.error(traceback.format_exc())

def main():
    try:
        print("Initializing Ice application...")
        app = CalculatorApp()
        sys.exit(app.main(sys.argv))
    except KeyboardInterrupt:
        print("\nReceived shutdown signal")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
