#!/usr/bin/env python
"""
NPC Generator
Cod version: v.0.0.8
----------------------------------------
Generates NPCs from a database stored in individual files within a folder structure.
Includes a Tkinter GUI with options to select parameters for all groups except Name and Personalities.
Streamlined Nationality handling to integrate with other parameters.
----------------------------------------
First update: 2024-02-29
First programmer: Martin Martinic
Last update: 2025-08-03
Last programmer: Grok
"""

import os
import random
import re
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Tuple, Optional, Union, Dict

import unicodedata


class NPCGenerator:
    """Generates Non-Playable Characters (NPCs) based on configuration and database files."""

    def __init__(self, config_file: str = "./config.txt", database_dir: str = "./database"):
        """Initialize NPC generator with configuration and database folder."""
        self.database_dir = database_dir
        self._load_config(config_file)
        self._load_database()
        self.all_groups = self._extract_groups()
        self.special_groups = self._extract_groups(self.config, '__')
        self.rarity_classes = self.extract_list(self.config, self.special_groups[0], '__')
        self.optional_groups = self.extract_list(self.config, self.special_groups[1], '__')
        self.multiple_groups = self.extract_list(self.config, self.special_groups[2], '__')
        self.conditioned_groups = self.extract_list(self.config, self.special_groups[3], '__')
        self.rarity_map: List[Tuple[str, int]] = []
        self.active_groups: List[str] = []
        self.groups_and_parameters: List[List[str]] = []
        self.locked_groups: set = set()

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

    def extract_list(self, data: Optional[str], group_name: str, delimiter: Optional[str] = None) -> List[str]:
        """Extract elements of a specific group from data string or file."""
        group_name = group_name.replace(' ', '_')
        if delimiter:
            pattern = rf'{delimiter}{group_name}{delimiter}\n((?:.*?\n)*?)/end'
            match = re.search(pattern, data)
            if not match:
                return ['None']
            items = match.group(1).strip().split('\n')
            items = [unicodedata.normalize('NFC', item.strip()) for item in items if item.strip()]
            return items if group_name in ['Personalities', 'Religion'] else \
                [item.replace(' ', '_') for item in items]

        subfolder_map = {
            'Name': 'Name',
            'Race': 'Race',
            'Sex': 'Sex'
        }

        subfolder = None
        for key in subfolder_map:
            if group_name.endswith(key):
                subfolder = subfolder_map[key]
                break

        if subfolder:
            file_path = os.path.join(self.database_dir, subfolder, f"{group_name}.txt")
            if os.path.exists(file_path):
                with open(file_path, encoding='utf-8') as f:
                    items = f.read().strip().split('\n')
                    items = [unicodedata.normalize('NFC', item.strip()) for item in items if item.strip()]
                    return items if group_name in ['Personalities', 'Religion'] else items

        file_path = os.path.join(self.database_dir, f"{group_name}.txt")
        if os.path.exists(file_path):
            with open(file_path, encoding='utf-8') as f:
                items = f.read().strip().split('\n')
                items = [unicodedata.normalize('NFC', item.strip()) for item in items if item.strip()]
                return items if group_name in ['Personalities', 'Religion'] else items

        for group in self.all_groups:
            sub_path = os.path.join(self.database_dir, group, f"{group_name}.txt")
            if os.path.exists(sub_path):
                with open(sub_path, encoding='utf-8') as f:
                    items = f.read().strip().split('\n')
                    items = [unicodedata.normalize('NFC', item.strip()) for item in items if item.strip()]
                    return items if group_name in ['Personalities', 'Religion'] else items

        return ['None']

    @staticmethod
    def _parse_special_group(group: str) -> List[str]:
        """Parse a special group string into its components."""
        return group.replace('_by_', '_').replace('__', '_').split('_')

    @staticmethod
    def _merge_rarity_lists(base_list: List[str], added_list: List[str]) -> List[str]:
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
            items = self.extract_list(None, items)
        if not items or items == ['None']:
            return ['None'] if force_select else []
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
        if not filtered_items and force_select and items and items != ['None']:
            selected = re.sub(rarity_pattern, '', random.choice(items))
            return [selected]
        return filtered_items if filtered_items or not force_select else []

    def _process_rarity_classes(self) -> None:
        """Parse rarity classes from config into rarity map."""
        self.rarity_map = []
        for rarity in self.rarity_classes:
            try:
                parts = self._parse_special_group(rarity)
                self.rarity_map.append([parts[0], int(parts[1])])
            except (IndexError, ValueError):
                pass

    def _process_optional_groups(self, locked_groups: set) -> None:
        """Remove optional groups based on probability, respecting locked groups."""
        for group in self.optional_groups:
            parts = self._parse_special_group(group)
            group_name = parts[0]
            if group_name in locked_groups:
                continue
            if int(parts[1]) <= random.randint(1, 100):
                if group_name in self.active_groups:
                    self.active_groups.remove(group_name)
                self.groups_and_parameters = [g for g in self.groups_and_parameters if g[0] != group_name]

    def _process_multiple_groups(self, locked_groups: set) -> None:
        """Handle groups that can have multiple parameters, preserving locked or conditioned parameters."""
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
                current_params = self.groups_and_parameters[idx][1:]
                if group_name in locked_groups or group_name in self.locked_groups:
                    if current_params and any(p != '' for p in current_params):
                        non_empty_params = [p for p in current_params if p != '']
                        self.groups_and_parameters[idx] = [group_name] + non_empty_params + [''] * (count - len(non_empty_params))
                    else:
                        self.groups_and_parameters[idx] = [group_name] + [''] * count
                elif group_name == 'Race' and 'Race_by_Nationality' in self.conditioned_groups and \
                     any(p[0] == 'Nationality' and len(p) > 1 and p[1] != '' for p in self.groups_and_parameters):
                    self.groups_and_parameters[idx] = [group_name] + [''] * count
                else:
                    self.groups_and_parameters[idx] = [group_name] + [''] * count

    def _process_conditioned_groups(self, select_params: bool = False,
                                    selected_params: Optional[Dict[str, str]] = None) -> None:
        """Handle conditioned groups by adjusting active groups and selecting parameters."""
        for group in self.conditioned_groups:
            parts = self._parse_special_group(group)
            main_group = parts[0]
            conditions = parts[1:]

            if select_params:
                if selected_params and main_group in selected_params and selected_params[main_group] != 'Any':
                    idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == main_group), None)
                    if idx is not None and self.groups_and_parameters[idx][1] != '':
                        continue

                condition_params = []
                for cond in conditions:
                    idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == cond), None)
                    if idx is not None and self.groups_and_parameters[idx][1] != '':
                        condition_params.append(
                            [param.replace(' ', '_') for param in self.groups_and_parameters[idx][1:]])
                    elif selected_params and cond in selected_params and selected_params[cond] != 'Any':
                        condition_params.append([selected_params[cond].replace(' ', '_')])
                    else:
                        condition_params.append(self.extract_list(None, cond))

                params = ['None']
                if main_group == 'Name':
                    combined_params = ['None']
                    for sex in condition_params[0]:
                        for race in condition_params[1]:
                            subgroup = f"{sex}_{race}_Name"
                            sub_params = self.extract_list(None, subgroup)
                            if sub_params != ['None']:
                                combined_params = self._merge_rarity_lists(combined_params, sub_params)
                    if combined_params == ['None']:
                        for sex in condition_params[0]:
                            sex_subgroup = f"{sex}Name"
                            sex_names = self.extract_list(None, sex_subgroup)
                            if sex_names != ['None']:
                                combined_params = self._merge_rarity_lists(combined_params, sex_names)
                        for race in condition_params[1]:
                            race_subgroup = f"{race}Name"
                            race_names = self.extract_list(None, race_subgroup)
                            if race_names != ['None']:
                                combined_params = self._merge_rarity_lists(combined_params, race_names)
                        if combined_params == ['None']:
                            combined_params = self.extract_list(None, main_group)
                    params = combined_params

                elif main_group == 'Race':
                    nationality = None
                    if selected_params and 'Nationality' in selected_params and selected_params['Nationality'] != 'Any':
                        nationality = selected_params['Nationality']
                    else:
                        idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == 'Nationality'), None)
                        if idx is not None and self.groups_and_parameters[idx][1] != '':
                            nationality = self.groups_and_parameters[idx][1]

                    if nationality:
                        if nationality.startswith('Resident of '):
                            nationality = nationality[len('Resident of '):]
                        nationality = nationality.replace(' ', '_')
                        expected_subgroup = f"Resident_of_{nationality}Race"
                        race_file = os.path.join(self.database_dir, 'Race', f"{expected_subgroup}.txt")
                        if os.path.exists(race_file):
                            params = self.extract_list(None, expected_subgroup)
                        else:
                            params = self.extract_list(None, 'Race')
                        if selected_params.get('Race', 'Any') != 'Any':
                            selected_race = re.sub(r'\(\w{1,3}\)$', '', selected_params['Race']).strip()
                            valid_races = [re.sub(r'\(\w{1,3}\)$', '', p).strip() for p in params]
                            if selected_race in valid_races:
                                params = [selected_race]
                            else:
                                params = ['None']
                    else:
                        params = self.extract_list(None, 'Race')

                    force_select = main_group in ['Race', 'Sex'] and any(condition_params)
                    self._select_parameters([main_group], params, force_select=force_select, overwrite=True)
                    if main_group == 'Race' and params != ['None'] and self.groups_and_parameters[idx][1] != '':
                        self.locked_groups.add(main_group)

                elif main_group == 'Sex':
                    params = self.extract_list(None, main_group)

                force_select = main_group in ['Race', 'Sex'] and any(condition_params)
                self._select_parameters([main_group], params, force_select=force_select, overwrite=True)

    def _select_parameters(self, groups: List[str], params: Optional[List[str]] = None,
                           force_select: bool = False, overwrite: bool = False) -> None:
        """Select parameters for given groups."""
        for group in groups:
            active_params = self._apply_rarity(params if params else group, force_select=force_select)
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group), None)
            if idx is not None:
                current_params = self.groups_and_parameters[idx][1:]
                used_indices = []
                if overwrite or not any(p != '' for p in current_params):
                    self.groups_and_parameters[idx] = [group] + [''] * len(current_params)
                    for i in range(1, len(current_params) + 1):
                        if active_params:
                            choice_idx = random.randint(0, len(active_params) - 1)
                            while choice_idx in used_indices and len(used_indices) < len(active_params):
                                choice_idx = random.randint(0, len(active_params) - 1)
                            used_indices.append(choice_idx)
                            self.groups_and_parameters[idx][i] = active_params[choice_idx]
                else:
                    for i, param in enumerate(current_params, start=1):
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
        self.locked_groups = set()

        self.rarity_map = []
        self.active_groups = self.all_groups.copy()
        self.groups_and_parameters = [[group, ''] for group in self.all_groups]
        locked_groups = set()

        if 'Nationality' in selected_params:
            group, param = 'Nationality', selected_params['Nationality']
            param = unicodedata.normalize('NFC', param)
            if param == 'Any':
                valid_params = self.extract_list(None, group)
                valid_params = [unicodedata.normalize('NFC', p) for p in valid_params]
                if valid_params and valid_params != ['None']:
                    param = random.choice(valid_params)
            param_clean = param if group in ['Nationality', 'Religion'] else param.replace(' ', '_')
            if group == 'Nationality' and param != 'None':
                if not param_clean.startswith('Resident of '):
                    param_clean = f"Resident of {param_clean}"
            valid_params = self.extract_list(None, group)
            valid_params = [unicodedata.normalize('NFC', p) for p in valid_params]
            valid_params_clean = [p.replace('_', ' ') if group in ['Nationality', 'Religion'] else p for p in valid_params]
            param_for_validation = re.sub(r'\(\w{1,3}\)$', '', param).strip()
            valid_params_clean = [re.sub(r'\(\w{1,3}\)$', '', p).strip() for p in valid_params_clean]
            if param != 'Any' and param_for_validation not in valid_params_clean and param != 'None':
                return []
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group), None)
            if idx is None:
                self.active_groups.append(group)
                self.groups_and_parameters.append([group, param_clean])
            else:
                self.groups_and_parameters[idx] = [group, param_clean]
            if param != 'Any' and param != 'None':
                locked_groups.add(group)

        for group, param in [(g, p) for g, p in selected_params.items() if g != 'Nationality']:
            param = unicodedata.normalize('NFC', param)
            if param == 'Any' and not (group == 'Race' and 'Race_by_Nationality' in self.conditioned_groups and
                                       any(p[0] == 'Nationality' and p[1] != '' for p in self.groups_and_parameters)):
                valid_params = self.extract_list(None, group)
                valid_params = [unicodedata.normalize('NFC', p) for p in valid_params]
                if valid_params and valid_params != ['None']:
                    param = random.choice(valid_params)
            param_clean = param if group in ['Nationality', 'Religion'] else param.replace(' ', '_')
            if group == 'Nationality' and param != 'None':
                if not param_clean.startswith('Resident of '):
                    param_clean = f"Resident of {param_clean}"
            valid_params = self.extract_list(None, group)
            valid_params = [unicodedata.normalize('NFC', p) for p in valid_params]
            valid_params_clean = [p.replace('_', ' ') if group in ['Nationality', 'Religion'] else p for p in valid_params]
            param_for_validation = re.sub(r'\(\w{1,3}\)$', '', param).strip()
            valid_params_clean = [re.sub(r'\(\w{1,3}\)$', '', p).strip() for p in valid_params_clean]
            if param != 'Any' and param_for_validation not in valid_params_clean and param != 'None':
                return []
            idx = next((i for i, g in enumerate(self.groups_and_parameters) if g[0] == group), None)
            if idx is None:
                self.active_groups.append(group)
                self.groups_and_parameters.append([group, param_clean])
            else:
                self.groups_and_parameters[idx] = [group, param_clean]
            if param != 'Any' and param != 'None':
                locked_groups.add(group)

        if 'Nationality' not in locked_groups and not any(
                g[0] == 'Nationality' and len(g) > 1 and g[1] != '' for g in self.groups_and_parameters):
            valid_nationalities = self.extract_list(None, 'Nationality')
            valid_nationalities = [unicodedata.normalize('NFC', p) for p in valid_nationalities]
            if valid_nationalities and valid_nationalities != ['None']:
                nationality = random.choice(valid_nationalities)
                if 'Nationality' not in self.active_groups:
                    self.active_groups.append('Nationality')
                    self.groups_and_parameters.append(['Nationality', nationality])
                else:
                    idx = next(i for i, g in enumerate(self.groups_and_parameters) if g[0] == 'Nationality')
                    self.groups_and_parameters[idx] = ['Nationality', nationality]

        if 'Race_by_Nationality' in self.conditioned_groups and \
           any(p[0] == 'Nationality' and len(p) > 1 and p[1] != '' for p in self.groups_and_parameters):
            locked_groups.add('Race')

        self._process_rarity_classes()
        if self.optional_groups and self.optional_groups[0] != 'None':
            self._process_optional_groups(locked_groups)
        if self.multiple_groups and self.multiple_groups[0] != 'None':
            self._process_multiple_groups(locked_groups)
        if self.conditioned_groups and self.conditioned_groups[0] != 'None':
            self._process_conditioned_groups(select_params=True, selected_params=selected_params)

        groups_to_select = [g for g in self.active_groups if not any(
            g == p[0] and len(p) > 1 and p[1] != '' for p in self.groups_and_parameters) and
            (g != 'Race' if 'Race_by_Nationality' in self.conditioned_groups and
             any(p[0] == 'Nationality' and len(p) > 1 and p[1] != '' for p in self.groups_and_parameters) else True)]
        self._select_parameters(groups_to_select)

        return self.groups_and_parameters

    def list_nationalities(self) -> List[str]:
        """List all possible nationalities from the database."""
        return self.extract_list(None, 'Nationality')


def print_npc(npc_data: List[List[str]], print_output: bool = False, save: bool = False) -> str:
    if not npc_data:
        output_str = "No NPC data generated. Check parameter validity.\n" + '-' * 120 + '\n'
    else:
        max_group_length = max(len(group[0]) for group in npc_data) if npc_data else 10
        output = []
        for group in npc_data:
            group_name = group[0]
            params = group[1:]
            params = [re.sub(r'\(\w{1,3}\)$', '', param).replace('_', ' ').strip() for param in params]
            formatted_params = ', '.join(params)
            output.append(f"{group_name:<{max_group_length}} : {formatted_params}")
        output_str = '\n' + '\n'.join(output) + '\n' + '-' * 120 + '\n'

    if print_output:
        print(output_str)
    if save:
        with open('./save.txt', 'a', encoding='utf-8') as f:
            f.write(output_str)

    return output_str


def update_race_dropdown(npc_gen: NPCGenerator, group_vars: Dict[str, tk.StringVar], dropdowns: Dict[str, ttk.Combobox],
                         *args) -> None:
    nationality = group_vars['Nationality'].get()
    if not nationality or nationality == 'Any':
        params = npc_gen.extract_list(None, 'Race')
        params = [re.sub(r'\(\w{1,3}\)$', '', p).strip() for p in params]
        dropdowns['Race']['values'] = ['Any'] + params
        dropdowns['Race'].set('Any')
        return

    nationality_clean = unicodedata.normalize('NFC', nationality)
    if nationality_clean.startswith('Resident of '):
        nationality_clean = nationality_clean[len('Resident of '):]
    nationality_clean = nationality_clean.replace(' ', '_')
    race_file = os.path.join(npc_gen.database_dir, 'Race', f"Resident_of_{nationality_clean}Race.txt")

    try:
        if os.path.exists(race_file):
            with open(race_file, encoding='utf-8') as f:
                races = f.read().strip().split('\n')
                races = [unicodedata.normalize('NFC', re.sub(r'\(\w{1,3}\)$', '', race).strip()) for race in races if
                         race.strip()]
        else:
            races = npc_gen.extract_list(None, 'Race')
            races = [re.sub(r'\(\w{1,3}\)$', '', race).strip() for race in races]

        dropdowns['Race']['values'] = ['Any'] + sorted(races)
        if dropdowns['Race'].get() not in ['Any'] + races:
            dropdowns['Race'].set('Any')
    except (FileNotFoundError, IOError):
        races = npc_gen.extract_list(None, 'Race')
        races = [re.sub(r'\(\w{1,3}\)$', '', race).strip() for race in races]
        dropdowns['Race']['values'] = ['Any'] + sorted(races)
        dropdowns['Race'].set('Any')


def generate_with_params(npc_gen: NPCGenerator, group_vars: Dict[str, tk.StringVar], dropdowns: Dict[str, ttk.Combobox],
                         output_text: scrolledtext.ScrolledText, npc_data: List[List[List[str]]]) -> None:
    """Generate an NPC with selected parameters and display it."""
    selected_params = {group: var.get() for group, var in group_vars.items()}
    if selected_params.get('Nationality', 'Any') != 'Any' and selected_params.get('Race', 'Any') != 'Any':
        nationality = selected_params['Nationality']
        if nationality.startswith('Resident of '):
            nationality = nationality[len('Resident of '):]
        nationality = nationality.replace(' ', '_')
        race_file = os.path.join(npc_gen.database_dir, 'Race', f"Resident_of_{nationality}Race.txt")
        if os.path.exists(race_file):
            with open(race_file, encoding='utf-8') as f:
                valid_races = [unicodedata.normalize('NFC', re.sub(r'\(\w{1,3}\)$', '', race).strip()) for race in
                               f.read().strip().split('\n')]
            selected_race = re.sub(r'\(\w{1,3}\)$', '', selected_params['Race']).strip()
            if selected_race not in valid_races:
                output_text.delete(1.0, tk.END)
                output_text.insert(tk.END,
                                   f"Error: Race '{selected_race}' not valid for Nationality '{selected_params['Nationality']}'.\n" + '-' * 120 + '\n')
                return
    if selected_params.get('Religion', 'Any') != 'Any':
        valid_religions = npc_gen.extract_list(None, 'Religion')
        valid_religions = [unicodedata.normalize('NFC', re.sub(r'\(\w{1,3}\)$', '', religion).strip()) for religion in
                           valid_religions]
        selected_religion = re.sub(r'\(\w{1,3}\)$', '', selected_params['Religion']).strip()
        if selected_religion not in valid_religions:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END,
                               f"Error: Religion '{selected_religion}' not found in database.\n" + '-' * 120 + '\n')
            return
    npc_data[0] = npc_gen.generate(selected_params)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, print_npc(npc_data[0], print_output=False))


def list_nationalities(npc_gen: NPCGenerator, output_text: scrolledtext.ScrolledText) -> None:
    """Display all available nationalities in the output text area."""
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\nAvailable Nationalities:\n")
    nationalities = npc_gen.list_nationalities()
    for nat in nationalities:
        output_text.insert(tk.END, f"- {nat.replace('_', ' ')}\n")
    output_text.insert(tk.END, '-' * 120 + '\n')


def save_npc(npc_data: List[List[List[str]]], output_text: scrolledtext.ScrolledText) -> None:
    """Save the current NPC data to a file and confirm in the output text area."""
    if npc_data[0]:
        print_npc(npc_data[0], save=True)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "NPC data saved to save.txt\n" + '-' * 120 + '\n')
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "No NPC data to save. Generate an NPC first.\n" + '-' * 120 + '\n')


def main():
    """Run the NPC generator with a Tkinter GUI."""
    root = tk.Tk()
    root.title("NPC Generator v.0.0.8")
    root.geometry("800x600")

    npc_gen = NPCGenerator()
    npc_data: List[List[List[str]]] = [[]]

    control_frame = ttk.Frame(root, padding="10")
    control_frame.pack(fill=tk.X)

    output_text = scrolledtext.ScrolledText(root, width=90, height=20, wrap=tk.WORD, font=("Courier", 10))
    output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    group_vars = {}
    dropdowns = {}
    excluded_groups = ['Name', 'Personalities']
    display_groups = [g for g in npc_gen.all_groups if g not in excluded_groups and g != 'Years']

    for i, group in enumerate(display_groups):
        label = ttk.Label(control_frame, text=f"{group}:")
        label.grid(row=i // 2, column=(i % 2) * 2, padx=5, pady=2, sticky=tk.E)
        params = npc_gen.extract_list(None, group)
        params = [unicodedata.normalize('NFC', re.sub(r'\(\w{1,3}\)$', '', p).strip()) for p in params]
        if group in ['Nationality', 'Religion']:
            params = [p.replace('_', ' ') for p in params]
        params = ['Any'] + sorted(params)
        var = tk.StringVar(root)
        var.set('Any')
        group_vars[group] = var
        dropdown = ttk.Combobox(control_frame, textvariable=var, values=params, state="readonly", width=30)
        dropdown.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=2, sticky=tk.W)
        dropdowns[group] = dropdown
        if group == 'Nationality':
            var.trace('w', lambda *args: update_race_dropdown(npc_gen, group_vars, dropdowns, *args))

    if 'Years' in npc_gen.all_groups:
        years_row = (len(display_groups) + 1) // 2
        label = ttk.Label(control_frame, text="Years:")
        label.grid(row=years_row, column=0, padx=5, pady=2, sticky=tk.E)
        params = npc_gen.extract_list(None, 'Years')
        params = [unicodedata.normalize('NFC', re.sub(r'\(\w{1,3}\)$', '', p).strip()) for p in params]
        params = ['Any'] + sorted(params)
        var = tk.StringVar(root)
        var.set('Any')
        group_vars['Years'] = var
        dropdown = ttk.Combobox(control_frame, textvariable=var, values=params, state="readonly", width=30)
        dropdown.grid(row=years_row, column=1, padx=5, pady=2, sticky=tk.W)
        dropdowns['Years'] = dropdown

    button_frame = ttk.Frame(control_frame)
    button_frame.grid(row=(len(display_groups) + 3) // 2, column=0, columnspan=4, pady=10)

    ttk.Button(button_frame, text="Generate",
               command=lambda: generate_with_params(npc_gen, group_vars, dropdowns, output_text, npc_data)).grid(row=0,
                                                                                                                 column=0,
                                                                                                                 padx=5,
                                                                                                                 pady=5)
    ttk.Button(button_frame, text="List Nationalities", command=lambda: list_nationalities(npc_gen, output_text)).grid(
        row=0, column=1, padx=5, pady=5)
    ttk.Button(button_frame, text="Save NPC", command=lambda: save_npc(npc_data, output_text)).grid(row=0, column=2,
                                                                                                    padx=5, pady=5)
    ttk.Button(button_frame, text="Exit", command=root.quit).grid(row=0, column=3, padx=5, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
