import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
import os
from source.common.logger import logger
import aiohttp
from source.config.config import global_config

agent = None

async def is_mcp_ready(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return resp.status in (200, 406)
    except Exception:
        return False
        
async def start_agent():
    mcp_url = "http://127.0.0.1:2333/mcp"
    for _ in range(10):
        if await is_mcp_ready(mcp_url):
            break
        await asyncio.sleep(0.5)
    else:
        raise RuntimeError("MCP server not ready")
    logger.debug("MCP server ready")

    llm = init_chat_model(
        model=global_config.get("Agent", "model"),
        model_provider=global_config.get("Agent", "model_provider"),
        base_url=global_config.get("Agent", "base_url"),
        api_key=global_config.get("Agent", "api_key")
    )

    client = MultiServerMCPClient({
        "whimbox": {
            "url": mcp_url,
            "transport": "streamable_http",
        }
    })
    tools = await client.get_tools()
    memory = MemorySaver()
    global agent
    agent = create_react_agent(llm, tools, checkpointer=memory, prompt=global_config.prompt, debug=False)
    logger.debug("MCP AGENT 初始化完成")

async def query_agent(text, thread_id="default", stream_callback=None, status_callback=None):
    global agent
    logger.debug("开始调用大模型")
    config = {"configurable": {"thread_id": thread_id}}
    input = {"messages": [{"role": "user", "content": text}]}
    
    full_response = ""
    
    # 通知开始思考
    if status_callback:
        status_callback("thinking")
    
    async for event in agent.astream_events(input, config=config):
        # print(f"Event: {event.get('event')}")
        # if event.get('event') in ['on_tool_start', 'on_tool_end', 'on_tool_error']:
        #     print(f"Tool Event Details: {event}")
        # elif 'tool' in str(event.get('event', '')).lower():
        #     print(f"Unknown Tool Event: {event}")
        
        # 处理不同类型的流式事件
        event_type = event.get("event")
        data = event.get("data", {})
        
        if event_type == "on_chat_model_stream":
            # 处理AI模型的流式输出
            chunk = data.get("chunk")
            if chunk and hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content
                if stream_callback and content.strip():  # 只发送非空内容
                    stream_callback(content)
        
        elif event_type == "on_tool_start":
            # 工具调用开始
            tool_name = event.get("name", "")
            if stream_callback:
                stream_callback(f"🔧 任务进行中，可以按“引号”键，随时终止任务\n")
            if status_callback:
                status_callback("on_tool_start", tool_name)
        
        elif event_type == "on_tool_end":
            # 工具调用结束
            tool_output = data.get("output", "")
            if stream_callback:
                stream_callback(f"💭 任务完成，总结成果中~\n")
            if status_callback:
                status_callback("on_tool_end", tool_name)
        
        elif event_type == "on_tool_error":
            # 工具调用错误
            error = data.get("error", "")
            if stream_callback:
                stream_callback(f"❌ 任务失败: {error}\n")
        
        elif event_type == "on_chat_model_start":
            # 开始生成回复
            if status_callback:
                status_callback("generating")
        
        elif event_type == "on_chain_end":
            # 整个链条结束，获取最终结果
            output = data.get("output")
            if output and hasattr(output, 'content'):
                # 如果有最终内容，确保包含在响应中
                if output.content and output.content not in full_response:
                    final_content = output.content
                    full_response += final_content
                    if stream_callback:
                        stream_callback(final_content)
    
    logger.debug("大模型调用完成")
    return full_response

def get_ai_message(resp):
    ai_msgs = []
    for msg in resp['messages']:
        if msg.type == 'ai':
            ai_msgs.append(msg.content)
    return '\n'.join(ai_msgs)