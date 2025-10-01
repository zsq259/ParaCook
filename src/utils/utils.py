import re
import json

def get_model(model_name):
    if "gemini" in model_name.lower():
        from src.agent.model.gemini_wrapper import GeminiWrapper
        return GeminiWrapper(name=model_name)
    # elif "deepseek" in model_name.lower():
    #     from src.agent.model.deepseek_wrapper import DeepSeekWrapper
    #     return DeepSeekWrapper(name=model_name)
    # elif "claude" in model_name.lower():
    #     from src.agent.model.claude_wrapper import ClaudeWrapper
    #     return ClaudeWrapper(name=model_name)
    else:
        from src.agent.model.gpt_wrapper import GPTWrapper
        return GPTWrapper(name=model_name)

def clean_text(text: str) -> str:
    # 移除提取 json 会报错的字符
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_json(text: str) -> dict|list:
    # json_regex = f'```json\s*([\s\S]*?)\s*```'
    # 去除 <think> 和 </think> 标签以及其中的内容
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 去除每行中 // 及其后的内容
    text = re.sub(r'//.*', '', text)

    json_regex = r'```json\s*([\s\S]*?)\s*```'
    matches = re.findall(json_regex, text)
    if matches and len(matches) > 0:
        json_data = matches[0].replace('```json', '').replace('```', '').strip()
        # .replace('\'', '\"')
        json_data = clean_text(json_data)
        try:
            parsed_json = json.loads(json_data)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON data: {e}") from e
    else:
        # text = text.replace("'", '"')
        text = clean_text(text)
        try:
            parsed_json = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON data: {e}") from e
        if isinstance(parsed_json, list) or isinstance(parsed_json, dict):
            return parsed_json
        else:
            raise ValueError(f"No JSON data found in the string: \033[38;5;214m{text}\033[0m")
            
# 将地图打印为字符画
def print_map(map_data):
    width = map_data["width"]
    height = map_data["height"]
    grid = [['   ']*width for _ in range(height)]
    for tile in map_data["tiles"]:
        x, y = tile["x"], tile["y"]
        ttype = tile["type"]
        if ttype == "obstacle":
            grid[y][x] = '███'  # 墙体
        elif ttype == "station":
            name = tile.get("name", "?")
            if "provides" in tile:
                # 食材分发器 D(*)
                provides = tile["provides"]
                if isinstance(provides, str):
                    provides = [provides]
                food = provides[0][0].upper()
                grid[y][x] = f"D({food})"
            elif "item" in tile:
                # 炊具或餐具
                item = tile["item"].lower()
                symbol = {
                    "pan": "Pn ", "pot": "Pt ", "plate": "Pl "
                }.get(item, item[:3].upper())
                grid[y][x] = symbol
            else:
                # 其他 station
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

    # 打印带边框的地图
    cell_width = 4  # 每个格子的内容宽度
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

    # 打印列编号（x轴）并标注
    x_label = ' ' * 6 + 'x→'
    col_header = ' ' * 6 + ''.join(f'{i:^{cell_width+1}}' for i in range(width))
    print(x_label)
    print(col_header)
    # 打印顶部边框
    print(' ' * 6 + corner_tl + (horizontal + cross_top) * (width - 1) + horizontal + corner_tr)
    for i, row in enumerate(grid):
        # 打印内容行，每个格子内容居中，左侧加行号（y轴）
        if i == 0:
            y_label = 'y↓'
        else:
            y_label = '  '
        content = f'{y_label}{i:>2}  ' + vertical + vertical.join(f"{str(cell):^{cell_width}}" for cell in row) + vertical
        print(content)
        # 打印中间分割线或底部边框
        if i < height - 1:
            print(' ' * 6 + cross_left + (horizontal + cross_center) * (width - 1) + horizontal + cross_right)
        else:
            print(' ' * 6 + corner_bl + (horizontal + cross_bottom) * (width - 1) + horizontal + corner_br)

    # 收集所有 station 缩写及其详细信息
    # 按坐标顺序逐个显示每个 station 的缩写和名字
    print("\nStation Abbreviation Legend:")
    for tile in sorted([t for t in map_data["tiles"] if t["type"] == "station"], key=lambda t: (t["y"], t["x"])):
        name = tile.get("name", "?")
        x, y = tile["x"], tile["y"]
        detail = ""
        if "provides" in tile:
            provides = tile["provides"]
            if isinstance(provides, str):
                provides = [provides]
            food = provides[0][0].upper()
            abbr = f"D({food})"
            detail = f"(Dispenser for {', '.join(provides)})"
        elif "item" in tile:
            item = tile["item"].lower()
            abbr = {
                "pan": "Pn ", "pot": "Pt ", "plate": "Pl "
            }.get(item, item[:3].upper())
            detail = f"(with {item})"
        else:
            symbol = {
                "chopping_board": "Cb ", "serving_window": "SW ", "sink": "Sk ", "stove": "St ", "table": "Tb ", "plate_return": "PR "
            }
            for k, v in symbol.items():
                if name.startswith(k):
                    abbr = v
                    break
            else:
                abbr = name[:3].upper()
            detail = ""
        print(f"  ({x},{y}) {abbr}: {name} {detail}")

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
    print_map(sample_map)
    print("Is map reachable?", check_reachability(sample_map))