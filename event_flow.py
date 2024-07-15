import time

class EventFlow:
    def __init__(self, event_controller):
        self.event_controller = event_controller

    def ring_and_pickup(self):
        self.event_controller.ring_telephone()
        # Logic to wait until the phone is picked up
        while not self.event_controller.phone_picked_up:  # Wait until the phone is picked up
            time.sleep(0.1)
        self.flow_start()  # Call flow_start once the phone is picked up

    def flow_start(self):
        self.event_controller.speak_response("Welcome stranger! Press 9 to continue the flow")
        self.wait_for_input()

    def wait_for_input(self):
        while True:
            if self.event_controller.controller.keypad_controller.key_pressed == '9':
                self.event_controller.speak_response("ACTIVATING!")
                break
            time.sleep(0.1)

    def run(self):
        self.ring_and_pickup()  # Start the ring and pickup process
        self.event_controller.run()

# Usage
if __name__ == '__main__':
    from event_controller import EventController
    event_controller = EventController()
    event_flow = EventFlow(event_controller)
    event_flow.run()
