import re
import json

def get_model(model_name):
    if "gemini" in model_name.lower():
        from src.agent.model.gemini_wrapper import GeminiWrapper
        return GeminiWrapper(name=model_name)
    elif "deepseek" in model_name.lower():
        from src.agent.model.deepseek_wrapper import DeepSeekWrapper
        return DeepSeekWrapper(name=model_name)
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
            raise ValueError(f"Error parsing JSON data: {e}")
    else:
        # text = text.replace("'", '"')
        text = clean_text(text)
        try:
            parsed_json = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON data: {e}")
        if isinstance(parsed_json, list) or isinstance(parsed_json, dict):
            return parsed_json
        else:
            raise ValueError(f"No JSON data found in the string: \033[38;5;214m{text}\033[0m")
            
# 将地图打印为字符画
def print_map(map_data):
    width = map_data["width"]
    height = map_data["height"]
    grid = [['.']*width for _ in range(height)]
    for tile in map_data["tiles"]:
        x, y = tile["x"], tile["y"]
        if tile["type"] == "obstacle":
            grid[y][x] = '#'
        elif tile["type"] == "station":
            if "provides" in tile:
                grid[y][x] = tile["provides"][0].upper()
            elif "item" in tile:
                grid[y][x] = tile["item"][0].upper()
            else:
                grid[y][x] = tile["name"][0].upper()
    for agent in map_data["agents"]:
        x, y = agent["x"], agent["y"]
        grid[y][x] = 'A'
    for row in grid:
        print(''.join(row))

if __name__ == "__main__":
    sample_map = {
    "name": "kitchen",
    "width": 10,
    "height": 8,
    "agents": [
        {
            "name": "agent1",
            "x": 4,
            "y": 7
        }
    ],
    "tiles": [
        {
            "x": 0,
            "y": 1,
            "type": "station",
            "name": "dispenser1",
            "provides": "tomato"
        },
        {
            "x": 7,
            "y": 7,
            "type": "station",
            "name": "dispenser2",
            "provides": "meat"
        },
        {
            "x": 9,
            "y": 6,
            "type": "station",
            "name": "dispenser3",
            "provides": "cheese"
        },
        {
            "x": 2,
            "y": 0,
            "type": "station",
            "name": "dispenser4",
            "provides": "lettuce"
        },
        {
            "x": 3,
            "y": 7,
            "type": "station",
            "name": "dispenser5",
            "provides": "bread"
        },
        {
            "x": 1,
            "y": 0,
            "type": "station",
            "name": "stove1",
            "item": "pan"
        },
        {
            "x": 9,
            "y": 4,
            "type": "station",
            "name": "stove2",
            "item": "pan"
        },
        {
            "x": 5,
            "y": 0,
            "type": "station",
            "name": "chopping_board1"
        },
        {
            "x": 5,
            "y": 7,
            "type": "station",
            "name": "chopping_board2"
        },
        {
            "x": 9,
            "y": 5,
            "type": "station",
            "name": "serving_window"
        },
        {
            "x": 0,
            "y": 0,
            "type": "station",
            "name": "sink"
        },
        {
            "x": 0,
            "y": 6,
            "type": "station",
            "name": "plate_return"
        },
        {
            "x": 6,
            "y": 3,
            "type": "station",
            "name": "table1",
            "item": "plate"
        },
        {
            "x": 5,
            "y": 6,
            "type": "station",
            "name": "table2",
            "item": "plate"
        },
        {
            "x": 4,
            "y": 6,
            "type": "station",
            "name": "table3"
        },
        {
            "x": 7,
            "y": 3,
            "type": "station",
            "name": "table4"
        },
        {
            "x": 1,
            "y": 5,
            "type": "obstacle",
            "name": "wall"
        },
        {
            "x": 2,
            "y": 3,
            "type": "obstacle",
            "name": "wall"
        }
    ]
}
    from src.utils.random_map import check_reachability
    print_map(sample_map)
    print("Is map reachable?", check_reachability(sample_map))