import yaml

input_list = []
# User input; the files that need to be merged
print('Enter the components you want to use, press enter when complete: ')
user_input = input()
while user_input != '':
    input_list.append(user_input)
    user_input = input()

# Ask user what name the recipe is gonna be
end_f = input('Name your recipe: ')


def merge_dict_list(*dict_list):
    output_dict = {}
    for d in dict_list:
        for key in d:
            try:
                output_dict[key].append(d[key])
            except KeyError:
                output_dict[key] = [d[key]]
    return output_dict


with open(end_f, 'w') as output_f:
    dict_list = []
    # Should walk trough the input_list list opening and merging one file at the time
    for i in input_list:
        try:
            with open(i, 'r') as f:
                f_dict = yaml.load(f)
                dict_list.append(f_dict)
                f.close()
        except FileNotFoundError:
            print('\nFile "', i, '" not found')
            change_f = input('Input the file again or press enter to remove: ')
            input_list.remove(i)
            if change_f != '':
                input_list.insert(input_list.count(i), change_f) #LINE OVERBODIG?
                print('\nSuccessfully changed to ', change_f)
                with open(change_f, 'r') as f:
                    f_dict = yaml.load(f)
                    dict_list.append(f_dict)
                    f.close()
        print(f_dict)
    f_data = yaml.dump(merge_dict_list(*dict_list))
    output_f.write(f_data)
    output_f.close()
