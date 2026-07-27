class State:
    def __init__(self, name: str):
        self.name = name
        # Maps (input_char, top_of_stack) -> (destination_state, string_to_write)
        self.transitions = dict() 
        
    def add_trans(self, character: str, termination: 'State', read: str, write: str) -> bool:
        if (character, read) in self.transitions:
            return False
        
        self.transitions[(character, read)] = (termination, write)
        return True
    
    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class DPDA:
    def __init__(self, alphabet: list, stack_alphabet: list, states: list[State], 
                 start_state: State, start_symbol: str, final_states: list[State]):
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.stack_alphabet = stack_alphabet
        self.start_symbol = start_symbol
    
    def transit_by_key(self, trans_key: tuple, stack: list, current_state: State) -> State | None:
        if trans_key in current_state.transitions:
            # Pop the required symbol
            stack.pop()
            
            # Push the new string onto the stack (in reverse order)
            write_str = current_state.transitions[trans_key][1]
            if write_str != "eps": 
                stack.extend(reversed(write_str))
                    
            # Move to the new state
            current_state = current_state.transitions[trans_key][0]
            
            print(f"State: {current_state.name}, Stack: ", end="")
            if len(stack) == 0:
                print("eps")
            else:
                print("".join(stack))
                
            return current_state
        return None

    def trace_path(self, s: str):
        if s == "eps":
            s = ""
            
        for c in s:
            if c not in self.alphabet:
                print("Invalid String")
                return
            
        print("\nParsing:")
        current_state = self.start_state
        parsed_ind = 0
        stack = list()
        
        # config -> (min_stack_len_ever, last_stack_len_when_visited)
        config_data = dict()
        
        stack.append(self.start_symbol)
        print(f"State: {current_state.name}, Stack: {self.start_symbol}")
        
        def check_loop(config: tuple, current_len: int) -> bool:
            if config not in config_data:
                config_data[config] = (current_len, current_len)
                return False
            min_ever, last_len = config_data[config]
            new_min = min(min_ever, current_len)
            if new_min >= last_len:
                return True
            config_data[config] = (new_min, current_len)
            return False
        
        while parsed_ind < len(s):
            if len(stack) == 0:
                print("Stack empty prematurely!")
                print("Result: Rejected")
                return
            
            trans_key = (s[parsed_ind], stack[-1])
            eps_key = ("eps", stack[-1])
            
            result = self.transit_by_key(trans_key, stack, current_state)
            if result is not None:
                current_state = result
                parsed_ind += 1
            else:
                # Try epsilon transition
                config = (current_state.name, stack[-1], parsed_ind)
                if check_loop(config, len(stack)):
                    print("Stuck in eps loop")
                    print("Result: Rejected")
                    return
                
                result = self.transit_by_key(eps_key, stack, current_state)
                if result is not None:
                    current_state = result
                else:
                    print("No valid transition found.")
                    print("Result: Rejected")
                    return

        # Post-input epsilon processing
        while True:
            if self.acc_condition(current_state, stack):
                print("Result: Accepted")
                return
            
            if len(stack) == 0:
                break
            
            config = (current_state.name, stack[-1], parsed_ind)
            if check_loop(config, len(stack)):
                print("Stuck in eps loop")
                print("Result: Rejected")
                return
            
            eps_key = ("eps", stack[-1])
            result = self.transit_by_key(eps_key, stack, current_state)
            if result is not None:
                current_state = result
            else:
                break
        
        print("Result: Rejected")
        
    def acc_condition(self, current_state: State, stack: list) -> bool:
        raise NotImplementedError("Subclasses must implement acc_condition")
    

class Final_DPDA(DPDA):
    def acc_condition(self, current_state: State, stack: list) -> bool:
        return current_state in self.final_states


class Empty_DPDA(DPDA):
    def acc_condition(self, current_state: State, stack: list) -> bool:
        return len(stack) == 0
    

def Validate_DPDA(states: list, alphabet: list, stack_alphabet: list, start_state: str, 
                  start_symbol: str, final_states: list, transitions: list, mode: str) -> DPDA | None:
    if start_state not in states:
        return None
    for s in final_states:
        if s not in states:
            return None

    name_to_state = {name: State(name) for name in states}
    
    for t in transitions:
        s0, character, read, s1, write = t
        if s0 not in states or s1 not in states:
            return None
        if character != "eps" and character not in alphabet:
            return None
        if read not in stack_alphabet:
            return None
                
        if not name_to_state[s0].add_trans(character, name_to_state[s1], read, write):
            return None
        
    # Verify Determinism (No eps/char conflict on the same stack symbol)
    for s in name_to_state.values():
        for stack_sym in stack_alphabet:
            if ("eps", stack_sym) in s.transitions:
                for c in alphabet:
                    if (c, stack_sym) in s.transitions:
                        return None
                    
    if mode.lower() == "final":
        return Final_DPDA(alphabet, stack_alphabet, list(name_to_state.values()), 
                          name_to_state[start_state], start_symbol,
                          [name_to_state[i] for i in final_states])
        
    return Empty_DPDA(alphabet, stack_alphabet, list(name_to_state.values()), 
                      name_to_state[start_state], start_symbol,
                      [name_to_state[i] for i in final_states])

if __name__ == "__main__":
    print("Enter DPDA properties in the following order:")
    print("1. States (space separated)")
    print("2. Input alphabet (space separated)")
    print("3. Stack alphabet (space separated)")
    print("4. Start state")
    print("5. Initial stack symbol")
    print("6. Final states (space separated)")
    print("7. Acceptance mode: [final/empty]")
    print("8. Number of transitions")

    try:
        states = input("States: ").split()
        alphabet = input("Input alphabet: ").split()
        stack_alphabet = input("Stack alphabet: ").split()
        start_state = input("Start state: ")
        start_symbol = input("Initial stack symbol: ")
        final_states = input("Final states: ").split()
        mode = input("Mode: ")
        number_of_transitions = int(input("Number of transitions: "))
        
        print("Enter transitions (Format: State_from Input_char Stack_top State_to Stack_write):")
        transitions = []
        for _ in range(number_of_transitions):
            transitions.append(tuple(input().split()))

        new_DPDA = Validate_DPDA(states, alphabet, stack_alphabet, start_state, start_symbol, final_states, transitions, mode)
        
        if new_DPDA is None:
            print("Invalid DPDA Configuration.")
            exit()
            
        q = int(input("\nNumber of test strings: "))
        for i in range(q):
            s = input(f"String {i+1}: ")
            new_DPDA.trace_path(s)
            
    except ValueError:
        print("Invalid input format.")
    except KeyboardInterrupt:
        print("\nExiting.")
