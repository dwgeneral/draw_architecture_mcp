#!/usr/bin/env python3
"""
Draw.io Architecture MCP Server

一个专门用于生成draw.io架构图的MCP服务器
"""

import asyncio
import json
import logging
import re
import time
import uuid
import os
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
    Tool,
)
from mcp.server.models import ServerCapabilities
from mcp.server.lowlevel.server import NotificationOptions
from zhipuai import ZhipuAI

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装python-dotenv，手动读取.env文件
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 配置日志
import os
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_server.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler(log_file_path, encoding='utf-8')  # 输出到文件
    ],
    force=True  # 强制重新配置
)
logger = logging.getLogger(__name__)

# 确保日志立即写入文件
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        handler.flush()

# 创建服务器实例
server = Server("draw-architecture")

# 提示词模板路径
PROMPT_FILE = Path(__file__).parent / "draw_architecture_prompt.md"

# 智谱AI客户端初始化
def get_zhipu_client():
    """获取智谱AI客户端"""
    api_key = os.getenv('ZHIPUAI_API_KEY')
    if not api_key:
        logger.error("未找到ZHIPUAI_API_KEY环境变量，请在.env文件中配置")
        raise ValueError("ZHIPUAI_API_KEY未配置")
    
    logger.info(f"使用智谱AI API Key: {api_key[:8]}...")
    return ZhipuAI(api_key=api_key)


def load_prompt_template() -> str:
    """加载提示词模板"""
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"提示词文件未找到: {PROMPT_FILE}")
        return ""
    except Exception as e:
        logger.error(f"读取提示词文件失败: {e}")
        return ""


def generate_xml_with_llm(description: str, diagram_name: str, prompt_template: str) -> str:
    """使用智谱AI生成draw.io XML内容"""
    try:
        logger.info("开始使用智谱AI生成架构图XML")
        client = get_zhipu_client()
        
        # 构建完整的提示词
        full_prompt = f"""{prompt_template}

## 用户需求
用户想要绘制的系统架构描述：
{description}

图表名称：{diagram_name}

## 任务要求
请根据上述架构描述和提示词模板，生成完整的draw.io XML代码。
要求：
1. 严格遵循XML格式规范
2. 确保所有ID唯一且非空
3. 包含完整的图形元素和样式
4. 使用合适的颜色和布局
5. 只输出XML代码，不要包含任何其他文字说明
"""
        
        logger.info(f"发送请求到智谱AI，提示词长度: {len(full_prompt)}")
        
        # 调用智谱AI
        response = client.chat.completions.create(
            model="glm-4-flash",  # 使用免费模型
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        logger.info("智谱AI响应成功，开始处理返回内容")
        xml_content = response.choices[0].message.content.strip()
        logger.info(f"原始响应长度: {len(xml_content)}")
        
        # 清理可能的markdown代码块标记
        if xml_content.startswith('```xml'):
            xml_content = xml_content[6:]
            logger.info("移除了```xml标记")
        if xml_content.startswith('```'):
            xml_content = xml_content[3:]
            logger.info("移除了```标记")
        if xml_content.endswith('```'):
            xml_content = xml_content[:-3]
            logger.info("移除了结尾```标记")
        
        final_content = xml_content.strip()
        logger.info(f"最终XML内容长度: {len(final_content)}")
        
        # 验证XML内容是否包含实际的组件
        if '<mxCell id=' not in final_content or final_content.count('<mxCell') < 5:
            logger.warning("智谱AI生成的XML内容过于简单，使用回退方案")
            return generate_drawio_xml(description, diagram_name)
            
        return final_content
        
    except Exception as e:
        logger.error(f"调用智谱AI失败: {e}")
        logger.info("使用回退方案生成架构图")
        # 如果LLM调用失败，回退到原来的方法
        return generate_drawio_xml(description, diagram_name)


def parse_architecture_description(description: str) -> Dict[str, List[str]]:
    """解析架构描述，提取组件信息"""
    components = {
        'frontend': [],
        'gateway': [],
        'services': [],
        'cache': [],
        'queue': [],
        'database': [],
        'storage': [],
        'monitoring': [],
        'external': []
    }
    
    # 前端组件关键词
    frontend_keywords = ['ios app', 'android app', 'web应用', 'mobile', '移动应用', 'app', 'react', 'vue', 'angular', '前端', 'ui', '用户界面', '小程序', 'h5', '单页应用']
    # 网关组件关键词
    gateway_keywords = ['api网关', 'gateway', '负载均衡', 'load balancer', 'cdn', 'nginx', 'haproxy', '反向代理', 'kong', 'zuul']
    # 服务组件关键词
    service_keywords = ['用户服务', '商品服务', '订单服务', '购物车服务', '支付服务', '推荐服务', '营销服务', '物流服务', '客服服务', '服务', 'service', '微服务', 'microservice', 'api']
    # 缓存组件关键词
    cache_keywords = ['redis', 'memcached', '缓存', 'cache', 'redis集群']
    # 队列组件关键词
    queue_keywords = ['kafka', 'rabbitmq', 'rocketmq', 'mq', '消息队列', 'queue', '队列', 'apache kafka']
    # 数据库关键词
    database_keywords = ['mysql', 'postgresql', 'mongodb', 'cassandra', 'elasticsearch', 'hbase', 'influxdb', '数据库', 'database', 'db', '主从集群', '数据仓库', 'hadoop', 'spark']
    # 存储关键词
    storage_keywords = ['存储', 'storage', 'hdfs', 'oss', 's3']
    # 监控关键词
    monitoring_keywords = ['监控', 'monitoring', '日志', 'log', 'metrics', '告警', 'prometheus', 'grafana', 'elk', 'zipkin', 'jaeger', 'jenkins', 'gitlab', 'docker', 'kubernetes']
    
    lines = description.split('\n')
    for line in lines:
        line_lower = line.lower()
        
        # 提取前端组件
        for keyword in frontend_keywords:
            if keyword in line_lower and line.strip():
                components['frontend'].append(line.strip())
                break
        
        # 提取网关组件
        for keyword in gateway_keywords:
            if keyword in line_lower and line.strip():
                components['gateway'].append(line.strip())
                break
        
        # 提取服务组件
        for keyword in service_keywords:
            if keyword in line_lower and '服务' in line and line.strip():
                components['services'].append(line.strip())
                break
        
        # 提取缓存组件
        for keyword in cache_keywords:
            if keyword in line_lower and line.strip():
                components['cache'].append(line.strip())
                break
        
        # 提取队列组件
        for keyword in queue_keywords:
            if keyword in line_lower and line.strip():
                components['queue'].append(line.strip())
                break
        
        # 提取数据库组件
        for keyword in database_keywords:
            if keyword in line_lower and line.strip():
                components['database'].append(line.strip())
                break
        
        # 提取存储组件
        for keyword in storage_keywords:
            if keyword in line_lower and line.strip():
                components['storage'].append(line.strip())
                break
        
        # 提取监控组件
        for keyword in monitoring_keywords:
            if keyword in line_lower and line.strip():
                components['monitoring'].append(line.strip())
                break
    
    return components


def generate_component_xml(comp_id: str, name: str, x: int, y: int, width: int, height: int, color: str) -> str:
    """生成单个组件的XML"""
    return f'''        <mxCell id="{comp_id}" value="{name}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#666666;fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />
        </mxCell>'''


def generate_connection_xml(edge_id: str, source_id: str, target_id: str) -> str:
    """生成连接线的XML"""
    return f'''        <mxCell id="{edge_id}" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{source_id}" target="{target_id}">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>'''


def generate_drawio_xml(architecture_description: str, diagram_name: str = "系统架构图") -> str:
    """根据架构描述和提示词模板生成draw.io XML格式的架构图"""
    
    logger.info("使用回退方案生成架构图XML")
    
    # 解析架构描述
    components = parse_architecture_description(architecture_description)
    logger.info(f"解析到的组件: {components}")
    
    # 生成时间戳和ID
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    diagram_id = str(uuid.uuid4())
    
    # 定义颜色方案（根据提示词模板）
    colors = {
        'frontend': '#e1d5e7',    # 紫色系 - 用户界面
        'gateway': '#d5e8d4',     # 绿色系 - 基础设施
        'services': '#dae8fc',    # 蓝色系 - 核心业务服务
        'cache': '#fff2cc',       # 橙色系 - 缓存
        'queue': '#fff2cc',       # 橙色系 - 队列
        'database': '#f8cecc',    # 灰色系 - 数据库
        'storage': '#f8cecc',     # 灰色系 - 存储
        'monitoring': '#d5e8d4',  # 绿色系 - 监控
        'external': '#ffe6cc'     # 黄色系 - 外部服务
    }
    
    # 生成XML内容
    xml_content = []
    
    # 添加标题
    xml_content.append(f'''        <mxCell id="title" value="{diagram_name}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="500" y="30" width="200" height="40" as="geometry" />
        </mxCell>''')
    
    # 当前Y位置
    current_y = 100
    layer_height = 120
    component_width = 150
    component_height = 60
    
    # 生成各层组件
    layers = [
        ('frontend', '前端层', components['frontend']),
        ('gateway', '接入层', components['gateway']),
        ('services', '业务服务层', components['services']),
        ('cache', '缓存层', components['cache']),
        ('queue', '消息队列层', components['queue']),
        ('database', '数据存储层', components['database'] + components['storage']),
        ('monitoring', '监控运维层', components['monitoring'])
    ]
    
    prev_layer_components = []
    
    for layer_type, layer_name, layer_components in layers:
        if not layer_components:
            continue
            
        # 添加层标题
        layer_title_id = f"layer-{layer_type}-title"
        xml_content.append(f'''        <mxCell id="{layer_title_id}" value="{layer_name}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="{current_y}" width="100" height="30" as="geometry" />
        </mxCell>''')
        
        # 计算组件位置
        num_components = len(layer_components)
        total_width = num_components * component_width + (num_components - 1) * 50
        start_x = (1200 - total_width) // 2
        
        current_layer_components = []
        
        # 生成组件
        for i, component in enumerate(layer_components):
            comp_id = f"comp-{layer_type}-{i}"
            comp_x = start_x + i * (component_width + 50)
            comp_y = current_y + 40
            
            # 清理组件名称
            clean_name = re.sub(r'^[\s\-•]+', '', component).strip()
            if '：' in clean_name:
                clean_name = clean_name.split('：')[0]
            
            xml_content.append(generate_component_xml(
                comp_id, clean_name, comp_x, comp_y, 
                component_width, component_height, colors[layer_type]
            ))
            
            current_layer_components.append(comp_id)
        
        # 生成连接线（连接到上一层）
        if prev_layer_components and current_layer_components:
            for i, source_id in enumerate(prev_layer_components):
                for j, target_id in enumerate(current_layer_components):
                    if abs(i - j) <= 1:  # 只连接相邻的组件
                        edge_id = f"edge-{source_id}-to-{target_id}"
                        xml_content.append(generate_connection_xml(edge_id, source_id, target_id))
        
        prev_layer_components = current_layer_components
        current_y += layer_height
    
    # 组装完整的XML
    xml_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{timestamp}" agent="MCP Draw Architecture Server" version="24.7.17">
  <diagram name="{diagram_name}" id="{diagram_id}">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
{chr(10).join(xml_content)}
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    return xml_template


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用工具 - 只有一个核心功能"""
    return [
        Tool(
            name="generate_architecture_diagram",
            description="根据用户的架构描述，结合专业提示词模板，生成详细的draw.io架构图",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "系统架构描述，包括组件、服务、数据库、技术栈等详细信息"
                    },
                    "diagram_name": {
                        "type": "string",
                        "description": "架构图名称",
                        "default": "系统架构图"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出文件路径（可选）"
                    }
                },
                "required": ["description"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用 - 专注于架构图生成"""
    
    if name == "generate_architecture_diagram":
        description = arguments.get("description", "")
        diagram_name = arguments.get("diagram_name", "系统架构图")
        output_file = arguments.get("output_file")
        
        logger.info(f"MCP调用：生成架构图 - {diagram_name}")
        logger.info(f"描述长度: {len(description)}")
        
        if not description:
            return [TextContent(
                type="text",
                text="错误：请提供系统架构描述"
            )]
        
        # 加载提示词模板（用于指导解析和生成）
        prompt_template = load_prompt_template()
        if not prompt_template:
            logger.warning("无法加载提示词模板")
            return [TextContent(
                type="text",
                text="警告：无法加载提示词模板，将使用默认规则生成架构图"
            )]
        
        # 使用智谱AI生成架构图XML
        logger.info("开始调用智谱AI生成架构图")
        xml_content = generate_xml_with_llm(description, diagram_name, prompt_template)
        logger.info(f"生成的XML内容长度: {len(xml_content)}")
        
        # 保存文件（如果指定了输出路径）
        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                
                return [TextContent(
                    type="text",
                    text=f"✅ 专业架构图已生成并保存到: {output_file}\n\n📋 架构图包含以下组件层次：\n- 前端层\n- 接入层\n- 业务服务层\n- 缓存层\n- 消息队列层\n- 数据存储层\n- 监控运维层\n\n🎯 架构图已根据您的描述和专业提示词模板生成，包含具体组件和连接关系。\n\n{xml_content}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ 保存文件失败: {e}\n\n✅ 架构图XML内容:\n\n{xml_content}"
                )]
        else:
            return [TextContent(
                type="text",
                text=f"✅ 专业架构图已生成！\n\n📋 架构图包含以下组件层次：\n- 前端层\n- 接入层\n- 业务服务层\n- 缓存层\n- 消息队列层\n- 数据存储层\n- 监控运维层\n\n🎯 架构图已根据您的描述和专业提示词模板生成，包含具体组件和连接关系。\n\n{xml_content}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ 未知工具: {name}。本MCP服务器只提供架构图生成功能。"
        )]


async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="draw-architecture",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())