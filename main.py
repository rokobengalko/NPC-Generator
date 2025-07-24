#!/usr/bin/env python
"""
# NPC generator
# Cod version: v.0.0.1
# _______________________________________
# Generates NPC from database in txt file
# _______________________________________
# First update: 29.2.2024.
# First programmer: Martin Martinic
# Last update: 3.3.2024.
# Last programmer: Martin Martinic
# _______________________________________
"""

import random
import itertools
import re


# _______________________________________
# .         - Any Character Except New Line
# \d        - Digit (0-9)
# \D        - Not a Digit (0-9)
# \w        - Word Character (a-z, A-Z, 0-9, _)
# \W        - Not a Word Character
# \s        - Whitespace (space, tab, newline)
# \S        - Not Whitespace
#
# \b        - Word Boundary
# \B        - Not a Word Boundary
# ^         - Beginning of a String
# $         - End of a String
#
# []        - Matches Characters in brackets
# [^ ]      - Matches Characters NOT in brackets
# |         - Either Or
# ( )       - Group
#
# Quantifiers
# *         - 0 or More
# +         - 1 or More
# ?         - 0 or One
# {3}       - Exact Number
# {3,4}     - Range of Numbers (Minimum, Maximum)
# _______________________________________


def extract_groups_from_database(database_str, delimiter='__'):
    """
    extracts list of all groups in database
    (used to search document for all groups and returns them inside of list)

    :param delimiter: Set of characters that define group set
    :param database_str: String of document from which list is extracted
    :return: list of all groups and number of them
    """

    tmp_pattern_str = (r'(' + delimiter + r'\w+' + delimiter + r')+')
    tmp_pattern = re.compile(tmp_pattern_str)
    tmp_database = re.findall(tmp_pattern, database_str, flags=0)

    out_groups = [ins_str.strip(delimiter) for ins_str in tmp_database]
    out_groups_length = len(out_groups)

    return out_groups, out_groups_length


def extract_list_from_database(database_str, group_name, delimiter='__'):
    """
    extracts list of elements inside of group and stores it inside of list
    (used to search document for certain group (Race) and returns all elements inside of it (dwarf, elf...))

    :param delimiter: Set of characters that define group set
    :param database_str: String of document from which list is extracted
    :param group_name: Name of group for witch list is extracted
    :return: list of all elements in the group and length of that group list
    """

    tmp_pattern_str = (delimiter + group_name + delimiter + r'(\n.+\s*)*/end')
    tmp_pattern = re.compile(tmp_pattern_str)
    tmp_database = re.search(tmp_pattern, database_str, flags=0)
    tmp_database_list = list(tmp_database.group(0).split('\n'))

    out_database_list = tmp_database_list[1:-1]
    out_list_length = len(out_database_list)

    return out_database_list, out_list_length


def clean_special_groups(group):
    """
    subtracts unnecessary characters from parameter: such as _by_ , and all other _
    than group all remaining words into list

    :param group: Parameter from which unnecessary characters are subtracted
    :return: List with group name and its specialties
    """

    tmp_group_string = group.replace('_by_', ' ')
    tmp_group_string = tmp_group_string.replace('_', ' ')
    tmp_group_and_specialties = re.findall(r'\w+', tmp_group_string)

    return tmp_group_and_specialties


def generate_all_combinations_of_sublists(subgroup_parameters_list, group_name):
    """
    generates all possible combinations of subgroup name for given set of conditional parameters

    :param group_name: name of group for which are made subgroup names
    :param subgroup_parameters_list: list of conditional parameters for given group
    :return: list of all possible subgroup names
    """

    tmp_subgroup_list = []

    # selects amount of parameters that will build subgroup
    for tmp_num_of_groups in range(len(subgroup_parameters_list)):
        # builds index list form list so that sublist can be called by its index
        tmp_group_indexes_list = list(range(len(subgroup_parameters_list)))

        # runs for every combination of groups dependent on for loop above
        for tmp_comb_of_groups in itertools.combinations(tmp_group_indexes_list, (tmp_num_of_groups + 1)):

            # list in which all combination of parameters for subgroup are listed
            tmp_subgroup_parameters_list_copy = []

            # selects all groups from current combination
            for tmp_group_index in tmp_comb_of_groups:
                tmp_subgroup_parameters_list_copy.append(subgroup_parameters_list[tmp_group_index])

            # generates list with all parameters from current combination
            for tmp_subgroup_block in itertools.product(*tmp_subgroup_parameters_list_copy):

                tmp_list = []
                for tmp_parameter_index in range(len(tmp_subgroup_block)):
                    tmp_list.append(tmp_subgroup_block[tmp_parameter_index])
                tmp_subgroup_list.append(tmp_list)

    for tmp_subgroup_index in range(len(tmp_subgroup_list)):
        tmp_subgroup_list[tmp_subgroup_index] = ''.join(tmp_subgroup_list[tmp_subgroup_index]) + group_name

    return tmp_subgroup_list


def merge_rarity_lists(base_list, added_list):
    """
    merge two lists, if one parameter is in both lists it takes rarity class form added_list

    :param base_list: list to which parameters are added
    :param added_list: list from which parameters are added
    :return: list that have parameters from both lists with rarity class prioritized by added_list
    """

    tmp_active_list = base_list + added_list

    for tmp_counter_base_list in range(len(base_list)):
        for tmp_counter_added_list in range(len(added_list)):

            # find rarity class of all parameters
            tmp_pattern = re.compile(r'(\(\w{1,3}\))$')
            tmp_base_list_rarity = re.findall(tmp_pattern, base_list[tmp_counter_base_list])
            tmp_added_list_rarity = re.findall(tmp_pattern, added_list[tmp_counter_added_list])

            # remove rarity class from parameter string
            try:
                tmp_base_list_element = base_list[tmp_counter_base_list].replace(tmp_base_list_rarity[0], '')
            except IndexError:
                tmp_base_list_element = base_list[tmp_counter_base_list]
            try:
                tmp_added_list_element = added_list[tmp_counter_added_list].replace(tmp_added_list_rarity[0], '')
            except IndexError:
                tmp_added_list_element = added_list[tmp_counter_added_list]

            # if there are multiple of the same parameter replace one in base list with the new one
            if tmp_base_list_element == tmp_added_list_element:
                tmp_active_list[tmp_counter_base_list] = added_list[tmp_counter_added_list]

    # remove duplicates from the list
    tmp_new_list = list(dict.fromkeys(set(tmp_active_list)))
    return tmp_new_list


class NonPlayableCharacter:

    def __init__(self):
        # defining local variables
        self.loc_all_groups_list = extract_groups_from_database(Database)[0]
        self.loc_special_groups = extract_groups_from_database(Config)

        # variables used for options inside of config.txt file
        # _______________________________________
        self.loc_rarity_classes = extract_list_from_database(Config, self.loc_special_groups[0][0])
        self.loc_optional_groups = extract_list_from_database(Config, self.loc_special_groups[0][1])
        self.loc_multiple_groups = extract_list_from_database(Config, self.loc_special_groups[0][2])
        self.loc_conditioned_groups = extract_list_from_database(Config, self.loc_special_groups[0][3])

        self.loc_all_rarity_classes = []

    # functions used for options inside of config.txt file
    # _______________________________________
    def rarity_classes(self, list_rarity_classes=False, get_rarity_corrected_list=False, group=None):
        """
        reads config.txt and connects rarity class defined in it with percentage given for it
        modifies given group or list in accordance to parameter rarity class for each parameter

        :param list_rarity_classes: if True reads config.txt and learns rarity classes
        :param get_rarity_corrected_list: if True modifies parameter list
        :param group: name of group or list for witch parameters are modified
        :return: list of parameters modified in accordance to their rarity class with
        """

        if list_rarity_classes:
            # all rarity classes are sorted in list with their percentage of occurring

            for tmp_rarity in self.loc_rarity_classes[0]:
                try:
                    self.loc_all_rarity_classes.append([clean_special_groups(tmp_rarity)[0],
                                                        int(clean_special_groups(tmp_rarity)[1])])
                except ValueError:
                    pass

        if get_rarity_corrected_list:

            tmp_all_active_parameters = []

            # check if input was database group or regular list
            try:
                tmp_all_parameters_from_group = extract_list_from_database(Database, group)[0]
            except TypeError:
                tmp_all_parameters_from_group = group

            # for every parameter in group check its rarity class and base on its chance to occur in active list,
            # form active lis of parameters
            for tmp_parameter in tmp_all_parameters_from_group:

                tmp_str_to_remove = ''
                tmp_pattern = re.compile(r'(\(\w{1,3}\))$')
                # extract rarity class  from parameter
                try:
                    tmp_rarity_class_str = re.findall(tmp_pattern, tmp_parameter)[0]
                    tmp_str_to_remove = tmp_rarity_class_str
                    tmp_rarity_class_str = tmp_rarity_class_str.replace('(', '')
                    tmp_rarity_class_str = tmp_rarity_class_str.replace(')', '')
                except IndexError:
                    tmp_rarity_class_str = ''

                # search if that rarity class is defined
                try:
                    tmp_rarity_class_index = [ins_rarity[0] for ins_rarity in self.loc_all_rarity_classes] \
                        .index(tmp_rarity_class_str)
                    tmp_rarity_class_int = self.loc_all_rarity_classes[tmp_rarity_class_index][1]
                except ValueError:
                    # check if rarity class is integer
                    try:
                        tmp_rarity_class_int = int(tmp_rarity_class_str)
                    # if not give it 100% chance of occurring
                    except ValueError:
                        tmp_rarity_class_int = 100

                if tmp_rarity_class_int >= random.randint(1, 100):
                    tmp_all_active_parameters.append(tmp_parameter.replace(tmp_str_to_remove, ''))

            return tmp_all_active_parameters

    def optional_groups(self):
        """
        check for optional groups and subtract unlucky ones from total parameter list

        :return: list of groups from witch are excluded unlucky groups
        """

        # input [[group, ''], [group_2, ''], [group_3, ''], ... ]
        # output [[group, ''], [group_3, ''], ... ]

        for tmp_parameter in self.loc_optional_groups[0]:
            # input Fear_by_80

            tmp_optional_group = clean_special_groups(tmp_parameter)
            # ['Fear', '80']
            tmp_optional_group_chance = random.randint(1, 100)

            # remove group from loc_groups_and_parameters_list if tmp_optional_group_chance
            # is less then chance specified in config.txt
            if int(tmp_optional_group[1]) <= tmp_optional_group_chance:
                try:
                    self.loc_groups_and_parameters_list.remove([tmp_optional_group[0], ''])
                except ValueError:
                    pass
                try:
                    self.loc_all_active_groups.remove(tmp_optional_group[0])
                except ValueError:
                    pass

    def multiple_groups(self):
        """
        check for groups that have multiple parameters than adds parameters in accordance to config file

        :return: added empty parameters to groups that deserve them
        """

        # input [[group, ''], [group_2, ''], [group_3, ''], ... ]
        # output [[group, '', ''], [group_2, '', '', ''], [group_3, ''], ... ]

        for tmp_parameter in self.loc_multiple_groups[0]:
            # input Race_by_20_min1max2

            tmp_multiple_group = clean_special_groups(tmp_parameter)
            # ['Race', '20', 'min1max2']
            # get range in which can be amount of parameters in group
            tmp_multiple_parameter_range = [int(n) for n in re.findall(r'\d+', tmp_multiple_group[2])]

            # count how many times will that parameter appear
            tmp_parameter_counter = tmp_multiple_parameter_range[0]

            tmp_optional_group_chance = random.randint(1, 100)
            tmp_counter = 0
            while (tmp_counter < (tmp_multiple_parameter_range[1] - tmp_multiple_parameter_range[0])) \
                    and (int(tmp_multiple_group[1]) >= tmp_optional_group_chance):
                tmp_parameter_counter += 1
                tmp_counter += 1
                tmp_optional_group_chance = random.randint(1, 100)

            # this is new list that will be substituted in place of old group parameter list
            tmp_multiple_parameter = [tmp_multiple_group[0]] + [''] * tmp_parameter_counter

            # if group is in group set than exchange its amount of parameters with new set
            try:
                tmp_groups_and_parameters_list = [ins_group[0] for ins_group in self.loc_groups_and_parameters_list]
                tmp_index = tmp_groups_and_parameters_list.index(tmp_multiple_group[0])

                self.loc_groups_and_parameters_list[tmp_index] = tmp_multiple_parameter
            except ValueError:
                pass

    def conditioned_groups(self, list_conditioned_groups=False, select_conditioned_parameters=False):
        """
        checks for conditioned groups and removes tam from normal set of groups then after
        all unconditioned groups are selected, checks if any of possible conditioned groups exists
        if so adds them to choosing pool

        :param list_conditioned_groups: if True removes conditioned group from normal set of groups
        :param select_conditioned_parameters: if True selects parameters from any existing conditioned group
        :return: list of all groups that are not conditioned and selects parameters for conditioned groups
        """

        for tmp_group in self.loc_conditioned_groups[0]:
            # input Name_by_Sex_Race
            tmp_group_and_subgroups = clean_special_groups(tmp_group)
            # ['Name', 'Sex', 'Race']
            tmp_active_group = tmp_group_and_subgroups[0]
            tmp_active_subgroups = tmp_group_and_subgroups[1:]

            if list_conditioned_groups:
                try:
                    self.loc_all_active_groups.remove(tmp_active_group)
                except ValueError:
                    pass

            if select_conditioned_parameters:

                # standard parameters for conditioned group
                tmp_all_active_parameters = extract_list_from_database(Database, tmp_active_group)[0]
                tmp_subgroup_parameters_list = []

                for tmp_subgroup in tmp_active_subgroups:

                    try:
                        tmp_subgroup_index = [ins_subgroup[0] for ins_subgroup in self.loc_groups_and_parameters_list] \
                            .index(tmp_subgroup)
                        tmp_subgroup_parameters_list.append(self.loc_groups_and_parameters_list[tmp_subgroup_index][1:])
                    except ValueError:
                        pass

                tmp_subgroup_list = []
                tmp_subgroup_list += (generate_all_combinations_of_sublists(tmp_subgroup_parameters_list,
                                                                            tmp_active_group))

                for tmp_subgroup2 in tmp_subgroup_list:

                    try:
                        tmp_subgroup_parameters = extract_list_from_database(Database, tmp_subgroup2, '==')[0]
                        tmp_all_active_parameters = \
                            merge_rarity_lists(tmp_all_active_parameters, tmp_subgroup_parameters)
                    except AttributeError:
                        pass

                self.select_parameter_for_groups([tmp_active_group], tmp_all_active_parameters)

    # _______________________________________

    def select_parameter_for_groups(self, active_groups=None, active_parameters=None):
        """
        used to select parameter for group

        :param active_groups: either single group name or list of groups
        :param active_parameters: either reads from database or list of parameters
        :return: list of groups with selected parameter
        """

        # default active_groups are ones which characteristics are not change with other functions
        if active_groups is None:
            active_groups = self.loc_all_active_groups

        for tmp_group in active_groups:

            # default active_parameters are ones for active_group
            if active_parameters is None:
                tmp_all_active_parameters = self.rarity_classes(False, True, tmp_group)
            else:
                tmp_all_active_parameters = self.rarity_classes(False, True, active_parameters)

            tmp_num_of_active_parameters = len(tmp_all_active_parameters)
            tmp_all_random_chances = []

            tmp_group_index = [ins_group_to_find[0] for ins_group_to_find in self.loc_groups_and_parameters_list] \
                .index(tmp_group)

            tmp_parameter_index = 0

            # for every element in sublist check for empty string, than replace it with random parameter
            for tmp_parameter in self.loc_groups_and_parameters_list[tmp_group_index]:

                if tmp_parameter == '' and tmp_parameter_index <= tmp_num_of_active_parameters:
                    # ensures that no single parameter will occur more than once
                    tmp_parameter_chance = random.randint(0, tmp_num_of_active_parameters - 1)
                    while tmp_parameter_chance in tmp_all_random_chances:
                        tmp_parameter_chance = random.randint(0, tmp_num_of_active_parameters - 1)

                    tmp_all_random_chances.append(tmp_parameter_chance)

                    self.loc_groups_and_parameters_list[tmp_group_index][tmp_parameter_index] = \
                        tmp_all_active_parameters[tmp_parameter_chance]

                tmp_parameter_index += 1

            self.loc_groups_and_parameters_list[tmp_group_index] = \
                [ins_parameter for ins_parameter in self.loc_groups_and_parameters_list[tmp_group_index] if
                 ins_parameter not in ['']]

    def __call__(self):

        # resetting non playable character specific lists every time it is called
        self.loc_all_rarity_classes = []  # list of all additional rarity classes
        self.loc_all_active_groups = self.loc_all_groups_list.copy()  # groups witch selection of parameters is not
        # conditioned by document config.txt
        self.loc_groups_and_parameters_list = []  # all groups and thai parameters in one list

        # add empty parameter to each group
        for tmp_group in self.loc_all_groups_list:
            self.loc_groups_and_parameters_list.append([tmp_group, ''])
            # [[group, ''], [group_2, ''], [group__3, ''], ... ]

        self.rarity_classes(True)
        if self.loc_optional_groups[0][0] != 'None':
            self.optional_groups()
        if self.loc_multiple_groups[0][0] != 'None':
            self.multiple_groups()
        if self.loc_conditioned_groups[0][0] != 'None':
            self.conditioned_groups(True)

        self.select_parameter_for_groups()

        if self.loc_conditioned_groups[0][0] != 'None':
            self.conditioned_groups(False, True)

        return self.loc_groups_and_parameters_list


def print_non_playable_character(npc_data, print1=False, save=False):
    """
    prints out or saves character scheat

    :param print1: if True print character scheat
    :param save: if True save character scheat to save.txt
    :param npc_data: list of groups ad parameters of nps
    :return: printed or saved character scheat
    """

    tmp_string = '\n'

    for tmp_group in npc_data:
        tmp_string += tmp_group[0] + ':\t' + ', '.join(tmp_group[1:]) + '\n'

    tmp_string += r'-' * 120 + '\n'

    if print1:
        print(tmp_string)

    if save:
        with open('./save.txt', 'a') as Save:
            Save.write(tmp_string)


if __name__ == '__main__':

    # _______________________________________
    with open('./config.txt', encoding='utf-8') as config:
        Config = config.read()

    with open('./database.txt', encoding='utf-8') as database:
        Database = database.read()
    # _______________________________________

    print('┌─┬┬─┬─┐┌──┐           ┌┐     \n'
          '││││┼│┌┘│┌─┼─┬─┬┬─┬┬┬─┐│└┬─┬┬┐\n'
          '││││┌┤└┐│└┐│┴┤│││┴┤┌┤┼└┤┌┤┼│┌┘\n'
          '└┴─┴┘└─┘└──┴─┴┴─┴─┴┘└──┴─┴─┴┘ \n')

    NPC = NonPlayableCharacter()
    npc = None
    control = input('n -\tgenerate new NPC\n'
                    's -\tsave NPC\n'
                    'help -\tcommands\n'
                    'esc -\tclose program\n'
                    ':')

    while control != 'esc':

        if control == 'n':
            npc = NPC()
            print_non_playable_character(npc, True)
        if control == 's':
            print_non_playable_character(npc, False, True)
        if control == 'help':
            print('n -\tgenerate new NPC\n'
                  's -\tsave NPC\n'
                  'help -\tcommands\n'
                  'esc -\tclose program\n'
                  'version: v.0.0.1\n')

        control = input(':')
