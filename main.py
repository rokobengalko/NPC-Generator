#!/usr/bin/env python
"""
NPC Generator
Cod version: v.0.0.1
----------------------------------------
Generates NPCs from a database stored in a text file.
----------------------------------------
First update: 2024-02-29
First programmer: Martin Martinic
Last update: 2024-03-03
Last programmer: Martin Martinic
"""

import random
import re
import itertools
from typing import List, Tuple, Optional, Union

class NPCGenerator:
    """Generates Non-Playable Characters (NPCs) based on configuration and database files."""

    def __init__(self, config_file: str = "./config.txt", database_file: str = "./database.txt"):
        """Initialize NPC generator with configuration and database files."""
        with open(config_file, encoding='utf-8') as f:
            self.config = f.read()
        with open(database_file, encoding='utf-8') as f:
            self.database = f.read()

        self.all_groups = self._extract_groups(self.database)
        self.special_groups = self._extract_groups(self.config)

        # Extract group configurations
        self.rarity_classes = self._extract_list(self.config, self.special_groups[0])
        self.optional_groups = self._extract_list(self.config, self.special_groups[1])
        self.multiple_groups = self._extract_list(self.config, self.special_groups[2])
        self.conditioned_groups = self._extract_list(self.config, self.special_groups[3])

        self.rarity_map = []
        self.active_groups = []
        self.groups_and_parameters = []

    def _extract_groups(self, data: str, delimiter: str = '__') -> List[str]:
        """Extract group names from a data string."""
        pattern = rf'({delimiter}\w+{delimiter})'
        groups = [g.strip(delimiter) for g in re.findall(pattern, data)]
        return groups

    def _extract_list(self, data: str, group_name: str, delimiter: str = '__') -> List[str]:
        """Extract elements of a specific group from a data string."""
        pattern = rf'{delimiter}{group_name}{delimiter}\n((?:.*?\n)*?)/end'
        match = re.search(pattern, data)
        if not match:
            return ['None']
        items = match.group(1).strip().split('\n')
        return [item for item in items if item.strip()]

    def _parse_special_group(self, group: str) -> List[str]:
        """Parse a special group string into its components."""
        group = group.replace('_by_', ' ').replace('_', ' ')
        return re.findall(r'\w+', group)

    def _generate_combinations(self, params: List[List[str]], group_name: str) -> List[str]:
        """Generate all possible subgroup name combinations."""
        combinations = []
        for r in range(1, len(params) + 1):
            for indices in itertools.combinations(range(len(params)), r):
                param_sets = [params[i] for i in indices]
                for combo in itertools.product(*param_sets):
                    combinations.append(''.join(combo) + group_name)
        return combinations

    def _merge_rarity_lists(self, base_list: List[str], added_list: List[str]) -> List[str]:
        """Merge two lists, prioritizing rarity from added_list."""
        combined = base_list + added_list
        rarity_pattern = re.compile(r'\(\w{1,3}\)$')
        result = {}
        for item in combined:
            base_item = re.sub(rarity_pattern, '', item)
            rarity = re.findall(rarity_pattern, item)
            result[base_item] = item if rarity else base_item
        return list(result.values())

    def _apply_rarity(self, items: Union[List[str], str]) -> List[str]:
        """Apply rarity classes to filter items based on their probability."""
        if isinstance(items, str):
            items = self._extract_list(self.database, items)
        
        filtered_items = []
        rarity_pattern = re.compile(r'\(\w{1,3}\)$')
        
        for item in items:
            rarity_match = re.findall(rarity_pattern, item)
            rarity_class = rarity_match[0][1:-1] if rarity_match else ''
            
            try:
                rarity_prob = next(r[1] for r in self.rarity_map if r[0] == rarity_class)
            except StopIteration:
                try:
                    rarity_prob = int(rarity_class)
                except ValueError:
                    rarity_prob = 100

            if rarity_prob >= random.randint(1, 100):
                filtered_items.append(re.sub(rarity_pattern, '', item))
        
        return filtered_items

    def _process_rarity_classes(self):
        """Parse rarity classes from config."""
        self.rarity_map = []
        for rarity in self.rarity_classes:
            try:
                parts = self._parse_special_group(rarity)
                self.rarity_map.append([parts[0], int(parts[1])])
            except (IndexError, ValueError):
                pass

    def _process_optional_groups(self):
        """Remove optional groups based on their probability."""
        for group in self.optional_groups:
            parts = self._parse_special_group(group)
            if int(parts[1]) <= random.randint(1, 100):
                self.active_groups.remove(parts[0])
                self.groups_and_parameters = [g for g in self.groups_and_parameters if g[0] != parts[0]]

    def _process_multiple_groups(self):
        """Handle groups that can have multiple parameters."""
        for group in self.multiple_groups:
            parts = self._parse_special_group(group)
            group_name, chance, minmax = parts[0], int(parts[1]), parts[2]
            min_count, max_count = map(int, re.findall(r'\d+', minmax))
            
            count = min_count
            for _ in range(max_count - min_count):
                if int(chance) >= random.randint(1, 100):
                    count += 1
            
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group_name), None)
            if idx is not None:
                self.groups_and_parameters[idx] = [group_name] + [''] * count

    def _process_conditioned_groups(self, list_groups: bool = False, select_params: bool = False, nationality: Optional[str] = None):
        """Handle conditioned groups by adjusting active groups and selecting parameters."""
        for group in self.conditioned_groups:
            parts = self._parse_special_group(group)
            main_group, conditions = parts[0], parts[1:]

            if list_groups:
                if main_group in self.active_groups:
                    self.active_groups.remove(main_group)

            if select_params:
                params = self._extract_list(self.database, main_group)
                condition_params = []
                for cond in conditions:
                    idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == cond), None)
                    if idx is not None:
                        condition_params.append(self.groups_and_parameters[idx][1:])
                    elif cond == 'Nationality' and nationality:
                        condition_params.append([nationality])

                subgroups = self._generate_combinations(condition_params, main_group)
                for subgroup in subgroups:
                    try:
                        sub_params = self._extract_list(self.database, subgroup, '==')
                        params = self._merge_rarity_lists(params, sub_params)
                    except AttributeError:
                        pass
                
                self._select_parameters([main_group], params)

    def _select_parameters(self, groups: List[str], params: Optional[List[str]] = None):
        """Select parameters for given groups."""
        for group in groups:
            active_params = self._apply_rarity(params if params else group)
            idx = next(i for i, g in enumerate(self.groups_and_parameters) if g[0] == group)
            
            used_indices = []
            for i, param in enumerate(self.groups_and_parameters[idx][1:], start=1):
                if param == '':
                    choice_idx = random.randint(0, len(active_params) - 1)
                    while choice_idx in used_indices:
                        choice_idx = random.randint(0, len(active_params) - 1)
                    used_indices.append(choice_idx)
                    self.groups_and_parameters[idx][i] = active_params[choice_idx]
            
            self.groups_and_parameters[idx] = [p for p in self.groups_and_parameters[idx] if p]

    def generate(self, nationality: Optional[str] = None) -> List[List[str]]:
        """Generate a new NPC, optionally with a specific nationality."""
        self.rarity_map = []
        self.active_groups = self.all_groups.copy()
        self.groups_and_parameters = [[group, ''] for group in self.all_groups]

        # Ensure Nationality is included if specified
        if nationality and 'Nationality' not in self.active_groups:
            self.active_groups.append('Nationality')
            self.groups_and_parameters.append(['Nationality', nationality])
        elif nationality:
            idx = next(i for i, g in enumerate(self.groups_and_parameters) if g[0] == 'Nationality')
            self.groups_and_parameters[idx] = ['Nationality', nationality]

        self._process_rarity_classes()
        if self.optional_groups and self.optional_groups[0] != 'None':
            self._process_optional_groups()
        if self.multiple_groups and self.multiple_groups[0] != 'None':
            self._process_multiple_groups()
        if self.conditioned_groups and self.conditioned_groups[0] != 'None':
            self._process_conditioned_groups(list_groups=True, nationality=nationality)

        self._select_parameters(self.active_groups)
        
        if self.conditioned_groups and self.conditioned_groups[0] != 'None':
            self._process_conditioned_groups(select_params=True, nationality=nationality)

        return self.groups_and_parameters

    def list_nationalities(self) -> List[str]:
        """List all possible nationalities from the database."""
        nationalities = self._extract_list(self.database, 'Nationality')
        return nationalities

def print_npc(npc_data: List[List[str]], print_output: bool = False, save: bool = False):
    """Print or save NPC data."""
    output = '\n' + '\n'.join(f"{group[0]}:\t{', '.join(group[1:])}" for group in npc_data)
    output += '\n' + '-' * 120 + '\n'

    if print_output:
        print(output)
    if save:
        with open('./save.txt', 'a', encoding='utf-8') as f:
            f.write(output)

def main():
    """Main function to run the NPC generator."""
    print("""
┌─┬┬─┬─┐┌──┐           ┌┐
││││┼│┌┘│┌─┼─┬─┬┬─┬┬┬─┐│└┬─┬┬┐
││││┌┤└┐│└┐│┴┤│││┴┤┌┤┼└┤┌┤┼│┌┘
└┴─┴┘└─┘└──┴─┴┴─┴─┴┘└──┴─┴─┴┘
    """)

    npc_gen = NPCGenerator()
    npc_data = None

    while True:
        control = input("n - generate new NPC\ns - save NPC\nN [nationality] - generate NPC with specific nationality\nl - list possible nationalities\nesc - close program\n:")
        if control == 'esc':
            break
        elif control == 'n':
            npc_data = npc_gen.generate()
            print_npc(npc_data, print_output=True)
        elif control.startswith('N '):
            nationality = control[2:].strip()
            npc_data = npc_gen.generate(nationality=nationality)
            print_npc(npc_data, print_output=True)
        elif control == 's':
            if npc_data:
                print_npc(npc_data, save=True)
        elif control == 'l':
            nationalities = npc_gen.list_nationalities()
            print("\nAvailable Nationalities:")
            for nat in nationalities:
                print(f"- {nat}")
            print('-' * 120 + '\n')

if __name__ == "__main__":
    main()
