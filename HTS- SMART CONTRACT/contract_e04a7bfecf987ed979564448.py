import smartpy as sp

class EventPlanner(sp.Contract):
    def __init__(self, initialOwner):
        self.init(
            owner = initialOwner,
            name_to_event = sp.map(
                tkey = sp.TString,
                tvalue = sp.TRecord(
                    date = sp.TString,
                    num_guests = sp.TIntOrNat
                )
            )
        )

    @sp.entry_point
    def set_date(self, params):
        sp.verify(sp.sender == self.data.owner)
        self.check_event(params.name)
        self.data.name_to_event[params.name].date = params.new_date

    @sp.entry_point
    def set_num_guests(self, params):
        sp.verify(sp.sender == self.data.owner)
        self.check_event(params.name)
        self.data.name_to_event[params.name].num_guests = params.new_num_guests

    @sp.entry_point
    def change_owner(self, params):
        sp.verify(sp.sender == self.data.owner)
        self.data.owner = params.new_owner

    def check_event(self, name):
        sp.if ~(self.data.name_to_event.contains(name)):
            self.data.name_to_event[name] = sp.record(date = "", num_guests = 0)

@sp.add_test(name = "AdvancedTest")
def test():
    scenario = sp.test_scenario()
    # Create HTML output for debugging
    scenario.h1("Event Planner")
    
    # Initialize test addresses
    firstOwner =  sp.test_account("tz1-firstOwner-address-1234")
    secondOwner = sp.test_account("tz1-secondOwner-address-5678")
    
    # Instantiate EventPlanner contract
    c1 = EventPlanner(firstOwner.address)
    
    # Print contract instance to HTML
    scenario += c1
    
    # Invoke EventPlanner entry points and print results to HTML
    scenario.h2("Set date for Tezos Meetup to 11-28-2017")
    scenario += c1.set_date(name = "Tezos Meetup", new_date = "11-28-2017").run(sender = firstOwner.address)
    
    scenario.h2("Set number of guests for Tezos Meetup to 80")
    scenario += c1.set_num_guests(name = "Tezos Meetup", new_num_guests = 80).run(sender = firstOwner.address)
    
    scenario.h2("Change owner")
    scenario += c1.change_owner(new_owner = secondOwner.address).run(sender = firstOwner.address)
    
    scenario.h2("New owner sets date for Tezos Meetup to 03-21-2019")
    scenario += c1.set_date(name = "Tezos Meetup", new_date = "03-21-2019").run(sender = secondOwner.address)
    
    scenario.h2("Old owner attempts to set date for Tezos Meetup")
    scenario += c1.set_date(name = "Tezos Meetup", new_date = "10-15-2018").run(sender = firstOwner.address, valid = False)
    
    # Verify expected results
    scenario.verify((c1.data.name_to_event["Tezos Meetup"].date) == '03-21-2019')
    scenario.verify((c1.data.name_to_event["Tezos Meetup"].num_guests) == 80)
    scenario.verify((c1.data.owner) == secondOwner.address)
