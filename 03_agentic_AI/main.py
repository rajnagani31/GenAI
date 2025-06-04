
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os
import json
import requests
load_dotenv()
client = OpenAI()

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return f"Somthing what wrong"

def run_command(cmd: str):
    result = os.system(cmd)
    return result

available_tools = {
    "get_weather": get_weather,
    "run_command":run_command,
}

# few-shot Prompting: The model is given sum exmple and direction
SYSTEM_PROMPT="""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.
    
    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    available tools:
    -'get_weather':tecks a city name as an input and return current weather city
    -'run_command':takes linux command as a string and executes the command and return the output after executing it.

    Exmples:
    user query:what is weather of surat city?
    output:{{'stap':"plan",'content':'user interseted in weather data'}}
    output:{{'stap':"plan",'from the available tools i should call get_weather'}}
    output:{{'stap':"action",'content':'user interseted in weather data'}}
    output:{{'stap':"observe",'output':55 degreey'}}
    Output:{{ "step": "output", "content": "The weather for gujrat seems to be 55 degrees." }}




    


"""
messages=[
    {'role':'system','content':SYSTEM_PROMPT},
]
while True:
    query=input(">>")
    messages.append({'role':'user','content':query})

    while True:
        response=client.chat.completions.create(
            model= "gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )


        messages.append({'role':'assistant','content':response.choices[0].message.content})
        parsed_response=json.loads(response.choices[0].message.content)
        
        # print(parsed_response)
        # break
        if parsed_response.get('step') == 'plan':
            print(f"  🧠:{ parsed_response.get('content')}")
            continue

        if parsed_response.get('step') == "action":
            tool_name=parsed_response.get("function")
            tool_input=parsed_response.get("input")
            
            print(f"  🛠️:Calling tool:{tool_name} With output:{tool_input}")
            if available_tools.get(tool_name) != False:
                output=available_tools[tool_name](tool_input)
                messages.append({"role":'user',"content":json.dumps({'stap':'observe','output':output})})
                continue
            
        if parsed_response.get("step") == "output":
            print("--->",parsed_response.get('content'))
            break    
