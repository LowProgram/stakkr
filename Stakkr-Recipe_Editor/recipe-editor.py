# coding: utf-8

import yaml

dict_list = []
input_list = []


def merge_dicts(*dict_list):
    # Merges all dicts in dict_list into a new one
    output_dict = {}
    for d in dict_list:
        for key in d:
            try:
                output_dict[key].append(d[key])
            except KeyError:
                output_dict[key] = [d[key]]
    return output_dict


def add_dict_list(i):
    # Tries to add recipe component to dict_list
    try:
        load_service(i)
    except FileNotFoundError:
        print('\nFile "', i, '" not found\n')
        change_f = input('\nInput the file again or press enter to remove: ')
        input_list.remove(i)
        if change_f != '':
            input_list.insert(input_list.count(i), change_f)
            print('\nSuccessfully changed to "', change_f, '"')
            load_service(i)


def recipe_create(input_list):
    # Opens the end file and adds the recipe components
    with open(end_f, 'w') as output_f:
        for i in input_list:
            add_dict_list(i)

        f_data = yaml.safe_dump(merge_dicts(*dict_list))
        output_f.write(f_data)
        output_f.close()


def load_service(i):
    # Loads the service into a dict
    with open(i, 'r') as f:
        f_dict = yaml.safe_load(f)
        print(f_dict)
        dict_list.append(f_dict)
        f.close()
    return f_dict


def input_services():
    # User input; the files that need to be merged
    service = input()
    while service != '':
        input_list.append(service)
        service = input()
    return input_list


print('Enter the components you want to use, press enter when complete: ')
input_list = input_services()

# Ask user what name the recipe is gonna be
end_f = input('Name your recipe: ')
recipe_create(input_list)
