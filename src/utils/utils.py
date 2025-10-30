import re
import json
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_model_wrapper(model_name):
    # from src.agent.model.gpt_wrapper import GPTWrapper
    # return GPTWrapper
    if "gemini" in model_name.lower():
        from src.agent.model.gemini_wrapper import GeminiWrapper
        return GeminiWrapper
    elif "llama" in model_name.lower():
        from src.agent.model.llama_wrapper import LLaMaWrapper
        return LLaMaWrapper
    # elif "deepseek" in model_name.lower():
    #     from src.agent.model.deepseek_wrapper import DeepSeekWrapper
    #     return DeepSeekWrapper
    # elif "claude" in model_name.lower():
    #     from src.agent.model.claude_wrapper import ClaudeWrapper
    #     return ClaudeWrapper
    else:
        from src.agent.model.gpt_wrapper import GPTWrapper
        return GPTWrapper

def clean_text(text: str) -> str:
    # Remove characters that cause errors when extracting JSON
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_json(text: str) -> dict|list:
    # json_regex = f'```json\s*([\s\S]*?)\s*```'
    # Remove <think> and </think> tags and their content
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Remove // comments from each line
    text = re.sub(r'//.*', '', text)

    json_regex = r'```json\s*([\s\S]*?)\s*```'
    matches = re.findall(json_regex, text)
    if matches and len(matches) > 0:
        json_data = matches[0].replace('```json', '').replace('```', '').strip()
        json_data = clean_text(json_data)
        json_data.replace("'", '"')
        try:
            parsed_json = json.loads(json_data)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON data: {e}") from e
    else:
        text = clean_text(text)
        text = text.replace("'", '"')
        try:
            parsed_json = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON data: {e}") from e
        if isinstance(parsed_json, list) or isinstance(parsed_json, dict):
            return parsed_json
        else:
            raise ValueError(f"No JSON data found in the string: \033[38;5;214m{text}\033[0m")

def print_map_ascii(map_data):
    width = map_data["width"]
    height = map_data["height"]
    grid = [['   ']*width for _ in range(height)]
    for tile in map_data["tiles"]:
        x, y = tile["x"], tile["y"]
        ttype = tile["type"]
        if ttype == "obstacle":
            grid[y][x] = '███'  # Wall
        elif ttype == "station":
            name = tile.get("name", "?")
            if "provides" in tile:
                provides = tile["provides"]
                if isinstance(provides, str):
                    provides = [provides]
                food = provides[0][0].upper()
                grid[y][x] = f"D({food})"
            elif "item" in tile:
                item = tile["item"]
                if isinstance(item, dict):
                    item_name = item.get("name", "?")
                elif isinstance(item, str):
                    item_name = item
                else:
                    item_name = str(item)
                item_name = item_name.lower()
                symbol = {
                    "pan": "Pn ", "pot": "Pt ", "plate": "Pl "
                }.get(item_name, item_name[:3].upper())
                grid[y][x] = symbol
            else:
                symbol = {
                    "chopping_board": "Cb ", "serving_window": "SW ", "sink": "Sk ", "stove": "St ", "table": "Tb ", "plate_return": "PR "
                }
                for k, v in symbol.items():
                    if name.startswith(k):
                        grid[y][x] = v
                        break
                else:
                    grid[y][x] = name[:3].upper()
    for idx, agent in enumerate(map_data["agents"], 1):
        x, y = agent["x"], agent["y"]
        grid[y][x] = f"A{idx} "

    cell_width = 4
    horizontal = '─' * cell_width
    vertical = '│'
    corner_tl = '┌'
    corner_tr = '┐'
    corner_bl = '└'
    corner_br = '┘'
    cross_top = '┬'
    cross_bottom = '┴'
    cross_left = '├'
    cross_right = '┤'
    cross_center = '┼'

    lines = []
    x_label = ' ' * 6 + 'x→'
    col_header = ' ' * 6 + ''.join(f'{i:^{cell_width+1}}' for i in range(width))
    lines.append(x_label)
    lines.append(col_header)
    lines.append(' ' * 6 + corner_tl + (horizontal + cross_top) * (width - 1) + horizontal + corner_tr)
    for i, row in enumerate(grid):
        if i == 0:
            y_label = 'y↓'
        else:
            y_label = '  '
        content = f'{y_label}{i:>2}  ' + vertical + vertical.join(f"{str(cell):^{cell_width}}" for cell in row) + vertical
        lines.append(content)
        if i < height - 1:
            lines.append(' ' * 6 + cross_left + (horizontal + cross_center) * (width - 1) + horizontal + cross_right)
        else:
            lines.append(' ' * 6 + corner_bl + (horizontal + cross_bottom) * (width - 1) + horizontal + corner_br)
    return '\n'.join(lines)

def get_map_legend(map_data):
    def dict_to_str(d, prefix=''):
        if isinstance(d, dict):
            parts = []
            for k, v in d.items():
                if isinstance(v, (dict, list)):
                    parts.append(f"{prefix}{k}: {dict_to_str(v, prefix=prefix+'  ')}")
                else:
                    parts.append(f"{prefix}{k}: {v}")
            return '{' + ', '.join(parts) + '}'
        elif isinstance(d, list):
            return '[' + ', '.join([dict_to_str(x, prefix=prefix+'  ') for x in d]) + ']'
        else:
            return str(d)

    legend_lines = []
    legend_lines.append("Station Abbreviation Legend:")
    for tile in sorted([t for t in map_data["tiles"] if t.get("type") == "station"], key=lambda t: (t.get("y", 0), t.get("x", 0))):
        name = tile.get("name", "?")
        x, y = tile.get("x", "?"), tile.get("y", "?")
        abbr = ""
        detail = []
        provides = tile.get("provides", None)
        if provides is not None:
            if isinstance(provides, str):
                provides_list = [provides]
            elif isinstance(provides, list):
                provides_list = provides
            else:
                provides_list = [str(provides)]
            food = str(provides_list[0])[0].upper()
            abbr = f"D({food})"
            detail.append(f"Dispenser for: {', '.join(map(str, provides_list))}")
        item = tile.get("item", None)
        if item is not None:
            if isinstance(item, dict):
                item_name = item.get("name", "?")
                abbr = {
                    "pan": "Pn ", "pot": "Pt ", "plate": "Pl "
                }.get(str(item_name).lower(), str(item_name)[:3].upper())
                detail.append(f"Item: {dict_to_str(item)}")
            elif isinstance(item, str):
                item_name = item
                abbr = {
                    "pan": "Pn ", "pot": "Pt ", "plate": "Pl "
                }.get(item_name.lower(), item_name[:3].upper())
                detail.append(f"Item: {item_name}")
            else:
                abbr = str(item)[:3].upper()
                detail.append(f"Item: {item}")
        if not abbr:
            symbol = {
                "chopping_board": "Cb ", "serving_window": "SW ", "sink": "Sk ", "stove": "St ", "table": "Tb ", "plate_return": "PR "
            }
            for k, v in symbol.items():
                if str(name).startswith(k):
                    abbr = v
                    break
            else:
                abbr = str(name)[:3].upper()
        for k, v in tile.items():
            if k in ("name", "x", "y", "type", "provides", "item"):
                continue
            detail.append(f"{k}: {dict_to_str(v)}")
        legend_lines.append(f"  ({x},{y}) {abbr}: {name} | " + ' | '.join(detail))

    legend_lines.append("\nAgent Info:")
    for idx, agent in enumerate(map_data.get("agents", []), 1):
        agent_str = dict_to_str(agent)
        legend_lines.append(f"  Agent{idx}: {agent_str}")
    return '\n'.join(legend_lines)


def draw_map_image(map_data):
    width = map_data["width"]
    height = map_data["height"]
    fig, ax = plt.subplots(figsize=(width/3, height/3))
    
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    
    ax.set_xticks(np.arange(width) + 0.5)
    ax.set_yticks(np.arange(height) + 0.5)

    ax.set_xticklabels(np.arange(width))
    ax.set_yticklabels(np.arange(height))

    ax.set_xticks(np.arange(width + 1), minor=True)
    ax.set_yticks(np.arange(height + 1), minor=True)

    ax.grid(which='minor', color='gray', linewidth=0.5)

    ax.tick_params(which='major', bottom=False, left=False)

    ax.set_aspect('equal')
    ax.invert_yaxis()

    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')

    from matplotlib.patches import Rectangle
    station_colors = {
        'dispenser': '#A3E635',      # Green
        'chopping_board': '#FBBF24', # Yellow
        'stove': '#F87171',          # Red
        'sink': '#60A5FA',           # Blue
        'serving_window': '#A78BFA', # Purple
        'table': "#979797",          # Gray
        'plate_return': '#34D399',   # Teal
    }
    for tile in map_data["tiles"]:
        x, y = tile["x"], tile["y"]
        ttype = tile["type"]
        if ttype == "obstacle":
            ax.add_patch(Rectangle((x, y), 1, 1, color='black'))
        elif ttype == "station":
            name = tile.get("name", "?")
            color = '#93C5FD' # Default light blue
            label = name[:2]
            if "item" in tile:
                item = tile["item"]
                if isinstance(item, dict):
                    item_name = item.get("name", "?")
                elif isinstance(item, str):
                    item_name = item
                else:
                    item_name = str(item)
                item_name = item_name.lower()
                label = {
                    "pan": "Pn", "pot": "Pt", "plate": "Pl"
                }.get(item_name, item_name[:2].upper())
            if 'dispenser' in name:
                color = station_colors['dispenser']
                label = 'D'
            elif name.startswith('chopping_board'):
                color = station_colors['chopping_board']
                label = 'Cb'
            elif name.startswith('stove'):
                color = station_colors['stove']
                label = 'St'
            elif name.startswith('sink'):
                color = station_colors['sink']
                label = 'Sk'
            elif name.startswith('serving_window'):
                color = station_colors['serving_window']
                label = 'SW'
            elif name.startswith('table'):
                color = station_colors['table']
                label = 'Tb'
            elif name.startswith('plate_return'):
                color = station_colors['plate_return']
                label = 'PR'
            ax.add_patch(Rectangle((x, y), 1, 1, color=color, alpha=0.7))
            ax.text(x+0.5, y+0.5, label, ha='center', va='center', fontsize=8, color='black')
    
    for idx, agent in enumerate(map_data["agents"], 1):
        x, y = agent["x"], agent["y"]
        ax.plot(x+0.5, y+0.5, 'ro', markersize=12)
        ax.text(x+0.5, y+0.5, f"A{idx}", ha='center', va='center', fontsize=10, color='white')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

if __name__ == "__main__":
    sample_map = {
    "name": "kitchen",
    "width": 10,
    "height": 8,
    "agents": [
        {
            "name": "agent1",
            "x": 4,
            "y": 6
        },
        {
            "name": "agent2",
            "x": 3,
            "y": 6
        }
    ],
    "tiles": [
        {
            "x": 0,
            "y": 1,
            "type": "station",
            "name": "dispenser1",
            "provides": "meat"
        },
        {
            "x": 7,
            "y": 0,
            "type": "station",
            "name": "dispenser2",
            "provides": "tomato"
        },
        {
            "x": 9,
            "y": 6,
            "type": "station",
            "name": "dispenser3",
            "provides": "fish"
        },
        {
            "x": 4,
            "y": 0,
            "type": "station",
            "name": "dispenser4",
            "provides": "prawn"
        },
        {
            "x": 3,
            "y": 7,
            "type": "station",
            "name": "dispenser5",
            "provides": "mushroom"
        },
        {
            "x": 9,
            "y": 5,
            "type": "station",
            "name": "dispenser6",
            "provides": "pasta"
        },
        {
            "x": 0,
            "y": 2,
            "type": "station",
            "name": "chopping_board1"
        },
        {
            "x": 4,
            "y": 7,
            "type": "station",
            "name": "chopping_board2"
        },
        {
            "x": 9,
            "y": 4,
            "type": "station",
            "name": "stove1",
            "item": "pan"
        },
        {
            "x": 0,
            "y": 6,
            "type": "station",
            "name": "stove2",
            "item": "pan"
        },
        {
            "x": 2,
            "y": 0,
            "type": "station",
            "name": "stove3",
            "item": "pot"
        },
        {
            "x": 0,
            "y": 4,
            "type": "station",
            "name": "stove4",
            "item": "pot"
        },
        {
            "x": 2,
            "y": 7,
            "type": "station",
            "name": "serving_window"
        },
        {
            "x": 1,
            "y": 0,
            "type": "station",
            "name": "sink"
        },
        {
            "x": 9,
            "y": 0,
            "type": "station",
            "name": "plate_return"
        },
        {
            "x": 3,
            "y": 5,
            "type": "station",
            "name": "table1",
            "item": "plate"
        },
        {
            "x": 6,
            "y": 2,
            "type": "station",
            "name": "table2",
            "item": "plate"
        },
        {
            "x": 7,
            "y": 3,
            "type": "station",
            "name": "table3"
        },
        {
            "x": 2,
            "y": 4,
            "type": "station",
            "name": "table4"
        },
        {
            "x": 6,
            "y": 4,
            "type": "obstacle",
            "name": "wall"
        },
        {
            "x": 3,
            "y": 3,
            "type": "obstacle",
            "name": "wall"
        }
    ]
}
    from src.utils.random_map import check_reachability
    print(print_map_ascii(sample_map))
    print(get_map_legend(sample_map))
    print("Is map reachable?", check_reachability(sample_map))