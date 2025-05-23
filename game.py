class Event:
    def __init__(self, description, safe_choice, risk_choice, safe_outcomes, risk_outcomes):
        self.description = description
        self.safe_choice = safe_choice
        self.risk_choice = risk_choice
        self.safe_outcomes = safe_outcomes
        self.risk_outcomes = risk_outcomes

class GameEvents:
    def __init__(self):
        self.events = [
            Event(
                description="IED detected ahead! How will you respond?",
                safe_choice="Send in Talon robot to investigate",
                risk_choice="Attempt manual approach",
                safe_outcomes={
                    'morale': 5,
                    'fuel': -5,
                    'robot_battery': -15,
                    'message': "Robot successfully cleared the route. Team confidence increased!"
                },
                risk_outcomes={
                    'morale': -20,
                    'fuel': -10,
                    'robot_battery': 0,
                    'message': "Close call! Team morale decreased significantly."
                }
            ),
            Event(
                description="Truck breaks down. What do you do?",
                safe_choice="Wait for maintenance team",
                risk_choice="Attempt field repair",
                safe_outcomes={
                    'morale': -5,
                    'fuel': -10,
                    'robot_battery': 10,
                    'message': "Maintenance fixed the issue but caused delays."
                },
                risk_outcomes={
                    'morale': -10,
                    'fuel': -20,
                    'robot_battery': 0,
                    'message': "Field repair partially successful but stressed the team."
                }
            ),
            Event(
                description="Talon robot battery low. Continue or stop to charge?",
                safe_choice="Stop to charge",
                risk_choice="Continue mission",
                safe_outcomes={
                    'morale': 5,
                    'fuel': -5,
                    'robot_battery': 50,
                    'message': "Robot fully charged. Team is well prepared."
                },
                risk_outcomes={
                    'morale': -15,
                    'fuel': 0,
                    'robot_battery': -25,
                    'message': "Robot died during crucial moment. Team stressed."
                }
            )
        ]
    
    def get_random_event(self):
        return random.choice(self.events)

    def handle_choice(self, event, is_safe_choice):
        outcomes = event.safe_outcomes if is_safe_choice else event.risk_outcomes
        return outcomes