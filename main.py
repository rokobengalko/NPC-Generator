#!/usr/bin/env python
"""
NPC Generator
Cod version: v.0.0.8
----------------------------------------
Generates NPCs from a database stored in individual files within a folder structure.
Includes a Tkinter GUI with options to select parameters for all groups before generation.
Streamlined Nationality handling to integrate with other parameters.
----------------------------------------
First update: 2024-02-29
First programmer: Martin Martinic
Last update: 2025-07-30
Last programmer: Grok
"""

import random
import re
import itertools
import os
from typing import List, Tuple, Optional, Union, Dict
import tkinter as tk
from tkinter import ttk, scrolledtext

class NPCGenerator:
    """Generates Non-Playable Characters (NPCs) based on configuration and database files."""

    def __init__(self, config_file: str = "./config.txt", database_dir: str = "./database"):
        """Initialize NPC generator with configuration and database folder."""
        self.database_dir = database_dir
        self._load_config(config_file)
        self._load_database()
        self.all_groups = self._extract_groups()
        self.special_groups = self._extract_groups(self.config, '__')
        self.rarity_classes = self._extract_list(self.config, self.special_groups[0], '__')
        self.optional_groups = self._extract_list(self.config, self.special_groups[1], '__')
        self.multiple_groups = self._extract_list(self.config, self.special_groups[2], '__')
        self.conditioned_groups = self._extract_list(self.config, self.special_groups[3], '__')
        self.rarity_map: List[Tuple[str, int]] = []
        self.active_groups: List[str] = []
        self.groups_and_parameters: List[List[str]] = []

    def _load_config(self, config_file: str) -> None:
        """Load configuration file."""
        try:
            with open(config_file, encoding='utf-8') as f:
                self.config = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {config_file} not found.")

    def _load_database(self) -> None:
        """Load database files from directory."""
        self.database = {}
        try:
            for filename in os.listdir(self.database_dir):
                if filename.endswith('.txt'):
                    group_name = filename[:-4]
                    file_path = os.path.join(self.database_dir, filename)
                    with open(file_path, encoding='utf-8') as f:
                        self.database[group_name] = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Database directory {self.database_dir} not found.")

    def _extract_groups(self, data: Optional[str] = None, delimiter: Optional[str] = None) -> List[str]:
        """Extract group names from database folder or config string."""
        if data and delimiter:
            pattern = rf'({delimiter}\w+{delimiter})'
            return [g.strip(delimiter) for g in re.findall(pattern, data)]
        return [filename[:-4] for filename in os.listdir(self.database_dir) if filename.endswith('.txt')]

    def _extract_list(self, data: Optional[str], group_name: str, delimiter: Optional[str] = None) -> List[str]:
        """Extract elements of a specific group from data string or file."""
        group_name = group_name.replace(' ', '_')
        if delimiter:
            pattern = rf'{delimiter}{group_name}{delimiter}\n((?:.*?\n)*?)/end'
            match = re.search(pattern, data)
            if not match:
                print(f"Warning: Group {group_name} not found in config.")
                return ['None']
            items = match.group(1).strip().split('\n')
            return [item.strip() for item in items if item.strip()] if group_name in ['Personalities', 'Religion'] else \
                   [item.strip().replace(' ', '_') for item in items if item.strip()]
        
        file_path = os.path.join(self.database_dir, f"{group_name}.txt")
        if os.path.exists(file_path):
            with open(file_path, encoding='utf-8') as f:
                items = f.read().strip().split('\n')
                return [item.strip() for item in items if item.strip()] if group_name in ['Personalities', 'Religion'] else \
                       [item.strip() for item in items if item.strip()]
        
        for group in self.all_groups:
            sub_path = os.path.join(self.database_dir, group, f"{group_name}.txt")
            if os.path.exists(sub_path):
                with open(sub_path, encoding='utf-8') as f:
                    items = f.read().strip().split('\n')
                    return [item.strip() for item in items if item.strip()] if group_name in ['Personalities', 'Religion'] else \
                           [item.strip() for item in items if item.strip()]
        return ['None']

    def _parse_special_group(self, group: str) -> List[str]:
        """Parse a special group string into its components."""
        return group.replace('_by_', '_').replace('__', '_').split('_')

    def _generate_combinations(self, params: List[List[str]], group_name: str) -> List[str]:
        """Generate all possible subgroup name combinations."""
        combinations = []
        for r in range(len(params), 0, -1):
            for indices in itertools.combinations(range(len(params)), r):
                param_sets = [params[i] for i in indices]
                for combo in itertools.product(*param_sets):
                    normalized_combo = [param.replace(' ', '_') for param in combo]
                    combinations.append('_'.join(normalized_combo) + group_name)
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

    def _apply_rarity(self, items: Union[List[str], str], force_select: bool = False) -> List[str]:
        """Apply rarity classes to filter items based on probability."""
        if isinstance(items, str):
            items = self._extract_list(None, items)
        
        filtered_items = []
        rarity_pattern = re.compile(r'\(\w{1,3}\)$')
        
        for item in items:
            rarity_match = re.findall(rarity_pattern, item)
            rarity_class = rarity_match[0][1:-1] if rarity_match else ''
            
            try:
                rarity_prob = next(r[1] for r in self.rarity_map if r[0] == rarity_class)
            except StopIteration:
                rarity_prob = int(rarity_class) if rarity_class.isdigit() else 100

            if rarity_prob >= random.randint(1, 100):
                filtered_items.append(re.sub(rarity_pattern, '', item))
        
        return filtered_items if filtered_items or not force_select or not items or items == ['None'] else \
               [re.sub(rarity_pattern, '', random.choice(items))]

    def _process_rarity_classes(self) -> None:
        """Parse rarity classes from config into rarity map."""
        self.rarity_map = []
        for rarity in self.rarity_classes:
            try:
                parts = self._parse_special_group(rarity)
                self.rarity_map.append([parts[0], int(parts[1])])
            except (IndexError, ValueError):
                pass

    def _process_optional_groups(self) -> None:
        """Remove optional groups based on probability."""
        for group in self.optional_groups:
            parts = self._parse_special_group(group)
            if int(parts[1]) <= random.randint(1, 100):
                self.active_groups.remove(parts[0])
                self.groups_and_parameters = [g for g in self.groups_and_parameters if g[0] != parts[0]]

    def _process_multiple_groups(self) -> None:
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

    def _process_conditioned_groups(self, list_groups: bool = False, select_params: bool = False, selected_params: Optional[Dict[str, str]] = None) -> None:
        """Handle conditioned groups by adjusting active groups and selecting parameters."""
        for group in self.conditioned_groups:
            parts = self._parse_special_group(group)
            main_group, conditions = parts[0], parts[1:]

            if list_groups and main_group in self.active_groups:
                self.active_groups.remove(main_group)

            if select_params:
                condition_params = []
                for cond in conditions:
                    idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == cond), None)
                    if idx is not None:
                        condition_params.append([param.replace(' ', '_') for param in self.groups_and_parameters[idx][1:]])
                    elif selected_params and cond in selected_params and selected_params[cond] != 'Any':
                        condition_params.append([selected_params[cond].replace(' ', '_')])

                params = ['None']
                if main_group == 'Name':
                    if conditions == ['Sex', 'Race']:
                        for sex in condition_params[0]:
                            for race in condition_params[1]:
                                subgroup = f"{sex}_{race}_Name"
                                try:
                                    sub_params = self._extract_list(None, subgroup)
                                    if sub_params != ['None']:
                                        params = self._merge_rarity_lists(params, sub_params)
                                        if params != ['None']:
                                            break
                                except AttributeError:
                                    pass
                            if params != ['None']:
                                break

                    if params == ['None'] and conditions == ['Sex', 'Race']:
                        combined_params = ['None']
                        for sex in condition_params[0]:
                            sex_subgroup = f"{sex}Name"
                            sex_names = self._extract_list(None, sex_subgroup)
                            if sex_names != ['None']:
                                combined_params = self._merge_rarity_lists(combined_params, sex_names)
                        for race in condition_params[1]:
                            race_subgroup = f"{race}Name"
                            race_names = self._extract_list(None, race_subgroup)
                            if race_names != ['None']:
                                combined_params = self._merge_rarity_lists(combined_params, race_names)
                        if combined_params != ['None']:
                            params = combined_params

                    if params == ['None']:
                        params = self._extract_list(None, main_group)

                else:
                    subgroups = self._generate_combinations(condition_params, main_group)
                    for subgroup in subgroups:
                        try:
                            sub_params = self._extract_list(None, subgroup)
                            if main_group == 'Race' and selected_params and 'Nationality' in selected_params and selected_params['Nationality'] != 'Any':
                                nationality = selected_params['Nationality'].replace(' ', '_')
                                if nationality.startswith('Resident_of_'):
                                    nationality = nationality[len('Resident_of_'):]
                                expected_subgroup = f"Resident_of_{nationality}Race"
                                if subgroup == expected_subgroup and sub_params != ['None']:
                                    params = sub_params
                            else:
                                params = self._merge_rarity_lists(params, sub_params)
                        except AttributeError:
                            print(f"Warning: Subgroup {subgroup} not found in database.")

                    if params == ['None']:
                        params = self._extract_list(None, main_group)

                force_select = main_group in ['Race', 'Sex'] and (selected_params or condition_params)
                self._select_parameters([main_group], params, force_select=force_select)

    def _select_parameters(self, groups: List[str], params: Optional[List[str]] = None, force_select: bool = False) -> None:
        """Select parameters for given groups."""
        for group in groups:
            active_params = self._apply_rarity(params if params else group, force_select=force_select)
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group), None)
            
            if idx is not None:
                used_indices = []
                for i, param in enumerate(self.groups_and_parameters[idx][1:], start=1):
                    if param == '' and active_params:
                        choice_idx = random.randint(0, len(active_params) - 1)
                        while choice_idx in used_indices and len(used_indices) < len(active_params):
                            choice_idx = random.randint(0, len(active_params) - 1)
                        used_indices.append(choice_idx)
                        self.groups_and_parameters[idx][i] = active_params[choice_idx]
                
                self.groups_and_parameters[idx] = [p for p in self.groups_and_parameters[idx] if p]

    def generate(self, selected_params: Optional[Dict[str, str]] = None) -> List[List[str]]:
        """Generate a new NPC, optionally with specific parameters for any group."""
        selected_params = selected_params or {}
        
        self.rarity_map = []
        self.active_groups = self.all_groups.copy()
        self.groups_and_parameters = [[group, ''] for group in self.all_groups]

        # Handle all parameters, including Nationality
        for group, param in selected_params.items():
            if param == 'Any':
                # For 'Any', randomly select a parameter
                valid_params = self._extract_list(None, group)
                if valid_params and valid_params != ['None']:
                    param = random.choice(valid_params)
                else:
                    continue
            param_clean = param.replace(' ', '_')
            if group == 'Nationality' and param != 'None':
                if not param_clean.startswith('Resident_of_'):
                    param_clean = f"Resident_of_{param_clean}"
            valid_params = self._extract_list(None, group)
            if param_clean not in valid_params and param != 'None':
                print(f"Error: Parameter '{param}' not found for group '{group}'.")
                return []
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group), None)
            if idx is None:
                self.active_groups.append(group)
                self.groups_and_parameters.append([group, param_clean])
            else:
                self.groups_and_parameters[idx] = [group, param_clean]

        # Ensure Nationality is set if not provided
        if not any(g[0] == 'Nationality' and len(g) > 1 and g[1] != '' for g in self.groups_and_parameters):
            valid_nationalities = self._extract_list(None, 'Nationality')
            if valid_nationalities and valid_nationalities != ['None']:
                nationality = random.choice(valid_nationalities)
                if 'Nationality' not in self.active_groups:
                    self.active_groups.append('Nationality')
                    self.groups_and_parameters.append(['Nationality', nationality])
                else:
                    idx = next(i for i, g in enumerate(self.groups_and_parameters) if g[0] == 'Nationality')
                    self.groups_and_parameters[idx] = ['Nationality', nationality]

        self._process_rarity_classes()
        if self.optional_groups and self.optional_groups[0] != 'None':
            self._process_optional_groups()
        if self.multiple_groups and self.multiple_groups[0] != 'None':
            self._process_multiple_groups()
        if self.conditioned_groups and self.conditioned_groups[0] != 'None':
            self._process_conditioned_groups(list_groups=True, selected_params=selected_params)

        # Select parameters only for groups not already set by user
        groups_to_select = [g for g in self.active_groups if not any(g == p[0] and len(p) > 1 and p[1] != '' for p in self.groups_and_parameters)]
        self._select_parameters(groups_to_select)
        
        if self.conditioned_groups and self.conditioned_groups[0] != 'None':
            self._process_conditioned_groups(select_params=True, selected_params=selected_params)

        return self.groups_and_parameters

    def list_nationalities(self) -> List[str]:
        """List all possible nationalities from the database."""
        return self._extract_list(None, 'Nationality')

def print_npc(npc_data: List[List[str]], print_output: bool = False, save: bool = False) -> str:
    """Format NPC data as a string with aligned formatting, optionally print or save."""
    if not npc_data:
        output_str = "No NPC data generated. Check parameter validity.\n" + '-' * 120 + '\n'
    else:
        max_group_length = max(len(group[0]) for group in npc_data) if npc_data else 10
        output = []
        for group in npc_data:
            group_name = group[0]
            params = group[1:]
            if group_name == 'Nationality':
                params = [param.replace('_', ' ') for param in params]
            formatted_params = ', '.join(params)
            output.append(f"{group_name:<{max_group_length}} : {formatted_params}")
        output_str = '\n' + '\n'.join(output) + '\n' + '-' * 120 + '\n'

    if print_output:
        print(output_str)
    if save:
        with open('./save.txt', 'a', encoding='utf-8') as f:
            f.write(output_str)
    
    return output_str

def main():
    """Run the NPC generator with a Tkinter GUI."""
    root = tk.Tk()
    root.title("NPC Generator v.0.0.8")
    root.geometry("800x600")

    npc_gen = NPCGenerator()
    npc_data = None

    # Frame for controls
    control_frame = ttk.Frame(root, padding="10")
    control_frame.pack(fill=tk.X)

    # Text area for output
    output_text = scrolledtext.ScrolledText(root, width=90, height=20, wrap=tk.WORD, font=("Courier", 10))
    output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Dropdowns for each group
    group_vars = {}
    dropdowns = {}
    for i, group in enumerate(npc_gen.all_groups):
        label = ttk.Label(control_frame, text=f"{group}:")
        label.grid(row=i//2, column=(i%2)*2, padx=5, pady=2, sticky=tk.E)
        params = npc_gen._extract_list(None, group)
        params = [p.replace('_', ' ') for p in params] if group in ['Nationality', 'Personalities', 'Religion'] else params
        params = ['Any'] + params
        var = tk.StringVar(root)
        var.set('Any')
        group_vars[group] = var
        dropdown = ttk.Combobox(control_frame, textvariable=var, values=params, state="readonly", width=30)
        dropdown.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=2, sticky=tk.W)
        dropdowns[group] = dropdown

    # Button frame
    button_frame = ttk.Frame(control_frame)
    button_frame.grid(row=len(npc_gen.all_groups)//2, column=0, columnspan=4, pady=10)

    def generate_npc():
        nonlocal npc_data
        npc_data = npc_gen.generate()
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, print_npc(npc_data, print_output=False))

    def generate_with_params():
        nonlocal npc_data
        selected_params = {group: var.get() for group, var in group_vars.items()}
        npc_data = npc_gen.generate(selected_params)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, print_npc(npc_data, print_output=False))

    def list_nationalities():
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "\nAvailable Nationalities:\n")
        nationalities = npc_gen.list_nationalities()
        for nat in nationalities:
            output_text.insert(tk.END, f"- {nat.replace('_', ' ')}\n")
        output_text.insert(tk.END, '-' * 120 + '\n')

    def save_npc():
        nonlocal npc_data
        if npc_data:
            print_npc(npc_data, save=True)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "NPC data saved to save.txt\n" + '-' * 120 + '\n')
        else:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "No NPC data to save. Generate an NPC first.\n" + '-' * 120 + '\n')

    # Buttons
    ttk.Button(button_frame, text="Generate with Parameters", command=generate_with_params).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(button_frame, text="List Nationalities", command=list_nationalities).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(button_frame, text="Save NPC", command=save_npc).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(button_frame, text="Exit", command=root.quit).grid(row=0, column=3, padx=5, pady=5)
    ttk.Button(button_frame, text="Generate NPC", command=generate_npc).grid(row=0, column=4, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
