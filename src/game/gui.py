import re
import streamlit as st
import json
import sys, os
import argparse
from src.utils.utils import get_map_legend, draw_map_image

st.set_page_config(layout="wide")

def ansi_to_html(text):
    ansi_map = {
        '\x1b[30m': '<span style="color:black">',
        '\x1b[31m': '<span style="color:red">',
        '\x1b[32m': '<span style="color:green">',
        '\x1b[33m': '<span style="color:orange">',
        '\x1b[34m': '<span style="color:blue">',
        '\x1b[35m': '<span style="color:purple">',
        '\x1b[36m': '<span style="color:cyan">',
        '\x1b[37m': '<span style="color:gray">',
        '\x1b[1m': '<span style="font-weight:bold">',
        '\x1b[4m': '<span style="text-decoration:underline">',
        '\x1b[7m': '<span style="background:gray">',
        '\x1b[40m': '<span style="background:black">',
        '\x1b[41m': '<span style="background:red">',
        '\x1b[42m': '<span style="background:green">',
        '\x1b[43m': '<span style="background:orange">',
        '\x1b[44m': '<span style="background:blue">',
        '\x1b[45m': '<span style="background:purple">',
        '\x1b[46m': '<span style="background:cyan">',
        '\x1b[47m': '<span style="background:gray">',
        '\x1b[0m': '</span>',
    }
    for code, html in ansi_map.items():
        text = text.replace(code, html)
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = text.replace('\n', '<br>')
    return text

def show_map(map_data):
    st.subheader("Map Visualization")
    img_buf = draw_map_image(map_data)
    st.image(img_buf, caption="Map Picture", width=500)
    legend = get_map_legend(map_data)
    st.text(legend)

def trans_actions_to_str(actions):
    if not actions:
        return "{}"
    result = "{\n"
    for agent, acts in actions.items():
        result += f'  "{agent}": [\n'
        for act in acts:
            act_str = json.dumps(act, ensure_ascii=False, separators=(", ", ": "))
            result += f'    {act_str},\n'
        if acts:
            result = result.rstrip(",\n") + "\n"
        result += "  ],\n"
    result = result.rstrip(",\n") + "\n}"
    return result


def action_editor(agent_names):
    st.subheader("Action Editor")
    
    if "actions" not in st.session_state:
        st.session_state["actions"] = {}
    
    actions_str = trans_actions_to_str(st.session_state["actions"])
    new_actions_str = st.text_area("Editable Action List (JSON format)", actions_str, height=200)
    
    try:
        new_actions = json.loads(new_actions_str)
        st.session_state["actions"] = new_actions
    except Exception:
        st.warning("Action list JSON format error, reverted to original content")

    st.write("Add New Action:")
    agent = st.selectbox("Choose Agent", agent_names)
    action_type = st.radio(
        "Choose Action Type",
        ["MoveTo", "Wait", "Interact", "Process", "Finish"],
        horizontal=True,
        key="action_type_radio"
    )
    
    params = {}
    if action_type == "MoveTo":
        target_str = st.text_input("Target Coordinates (x,y)", key="move_to_input")
        if target_str:
            try:
                params["target"] = [int(x.strip()) for x in target_str.split(",")]
            except Exception:
                st.warning("Error in coordinate format, should be x,y")
    elif action_type == "Wait":
        params["duration"] = st.number_input("Wait Duration", min_value=1, value=1, key="wait_input")
    elif action_type in ["Interact", "Process"]:
        target_obj = st.text_input("Target Object Name", key="target_obj_input")
        params["target"] = target_obj.strip()

    if st.button("Add Action"):
        if action_type == "MoveTo":
            if "target" not in params or not isinstance(params["target"], list) or len(params["target"]) != 2:
                st.warning("Error in MoveTo coordinates, should be x,y")
                return
        elif action_type in ["Interact", "Process"]:
            if not params.get("target"):
                st.warning("Target object name cannot be empty")
                return

        new_action = {"action": action_type, **params}
        if agent not in st.session_state["actions"]:
            st.session_state["actions"][agent] = []
        st.session_state["actions"][agent].append(new_action)
        st.success(f"Successfully added action for {agent}: {new_action}")
        st.rerun()

def main():
    st.title("ParaCook Testing GUI")

    world_json_path = "tmp/world.json"
    actions_path = "tmp/actions.json"
    log_path = "tmp/log.txt"

    if st.button("Clear All States and Refresh"):
        st.session_state.clear()
        for f in [world_json_path, actions_path]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        with open(log_path, 'w', encoding='utf-8') as log_f:
            log_f.write("")
        st.rerun()

    parser = argparse.ArgumentParser()
    parser.add_argument('--recipes', type=str, default="")
    parser.add_argument('--orders', type=str, default="")
    parser.add_argument('--map_data', type=str, required=True)
    args, _ = parser.parse_known_args()

    col1, col2 = st.columns([2, 2])
    with col1:
        
        if os.path.exists(world_json_path):
            with open(world_json_path, "r", encoding="utf-8") as wf:
                map_data = json.load(wf)
        else:
            map_data = json.loads(args.map_data)
        agent_names = [agent["name"] for agent in map_data["agents"]]
        show_map(map_data)
    with col2:
        st.subheader("Current Test Recipes and Orders")
        st.markdown(f"**Recipes:** {args.recipes if args.recipes else 'None'}")
        st.markdown(f"**Orders:** {args.orders if args.orders else 'None'}")
        action_editor(agent_names)
        if st.button("Execute Action Plan"):
            
            with open(actions_path, "w", encoding="utf-8") as f:
                json.dump(st.session_state["actions"], f, ensure_ascii=False, indent=2)
            st.success("Successfully saved actions to actions.json (Human.py will automatically detect and execute)")
        
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as log_f:
                log_content = log_f.read()
            st.subheader("Execution Result Log (tmp/log.txt)")
            if log_content.strip():
                log_html = ansi_to_html(log_content)
                st.markdown(log_html, unsafe_allow_html=True)
            else:
                st.info("No execution result log yet.")
        else:
            st.info("No execution result log yet.")

if __name__ == "__main__":
    main()