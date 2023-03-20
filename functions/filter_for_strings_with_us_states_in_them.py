def filter_for_strings_with_us_states_in_them(strings: list):
    """
    This function takes in a list of strings and filters out only those which contain the name of a US state.
    """
    us_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 
                'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 
                'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 
                'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
                'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 
                'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 
                'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
    
    filtered_strings = []
    for string in strings:
        for state in us_states:
            if state in string:
                filtered_strings.append(string)
                break
    
    return filtered_strings
