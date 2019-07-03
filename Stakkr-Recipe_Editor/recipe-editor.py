import yaml

input_list = []
header_list = ['service', 'proxy', 'aliases', 'services', 'commands', 'messages']
# User input; the files that need to be merged
print('Enter the components you want to use: ')
user_input = input()
while user_input != '':
    input_list.append(user_input)
    user_input = input()

# Ask user what name the recipe is gonna be
end_f = input('Name your recipe: ')

def merge_data(f_dict : str):
    for header in header_list:
        for i in f_dict[header]:
           

with open(end_f, 'w') as output_f:
    # Should walk trough the input_list list opening and merging one file at the time
    for i in input_list:
        with open(i, 'r') as f:
            f_dict = yaml.load(f)
            f.close()
            # First file determines format
            if i == input_list[0]:
                f_data = yaml.dump(f_dict)
                output_f.write(f_data)

            # Search data and merge this into the output_f
            else:
                merge_data(f_dict)
