from openai import OpenAI
from dotenv import load_dotenv
import os
import requests 
import json

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
client=OpenAI(api_key=api_key)


def get_weather(city:str):
    url=f"https://wttr.in/{city}"
    response=requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    

def run_command(command):
    print(command)
    result=os.system(command=command)
    return result


available_tools={
    "get_weather":{
        "fn":get_weather,
        "description":"Takes city name as input and returns the current weather for that city"
    },
    "run_command":{
        "fn":run_command,
        "description":"Takes a command and execute that command on users system"
    }
}
system_prompt=f'''
You are an helpful AI assistant who is specialised in resolving user Query.You work on start,plan,action,observe mode.
For the given user query and available tools,plan the step by step execution ,based on the planning select the relevant tool from available tools,
and based on the tool selection you perform an action to call the tool.
Wait for the observation and based on the observation follow the tool call resolve query 
Rules :
-follow the output JSON format
-Always perform ne step at a time and wait for next
-Carefully analyse the query

Output JSON Format:
{{
"step":"string",
"content":"string",
"function":"The name of the function if the step is action",
"input":"The input parameter for the function"
}}
Available Tools:
get_weather:Tool to get weather of a city
run_command :Takes a command as input execute on system and returns output

Examples:
UserQuery:What is the weather of New York?
Output:{{"step":"plan","content":"The user is interested in knowing about current weather"}}
Output:{{"step":"plan","content":"From the available tools I should call get_weather"}}
Output:{{"step":"action","function":"get_weather","input":"new york"}}
Output:{{"step":"observe","output":"12 degress Cel"}}
Output:{{"step":"output","content":"The weather for new york seems to be 12 degrees."}}
'''


messages=[{"role":"system","content":system_prompt}]
while True:
    user_query=input('>')
    messages.append({"role":"user","content":user_query})
    while True:
        response=client.chat.completions.create(
            model="gpt-4o",
            response_format={"type":"json_object"},
            messages=messages
        )
        parsed_output=json.loads(response.choices[0].message.content)
        messages.append({"role":"assistant","content":json.dumps(parsed_output)})

        if parsed_output.get("step")=="plan":
            print(f"brain:{parsed_output.get("content")}")
            continue
        if parsed_output.get("step")=="action":
            tool_name=parsed_output.get("function") 
            tool_input=parsed_output.get("input")

            if available_tools.get(tool_name,False)!=False:
                output=available_tools[tool_name].get("fn")(tool_input)
                messages.append({"role":"assistant","content":json.dumps({"step":"observe","output":output})})
                continue
        if parsed_output.get("step")=="output":
            print(f"{parsed_output.get("content")}")
            break