#!/usr/bin/env python3
"""
Draw.io Architecture MCP Server

一个专门用于生成draw.io架构图的MCP服务器
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from mcp.server.models import ServerCapabilities
from mcp.shared.context import RequestContext
from mcp.server.lowlevel.server import NotificationOptions

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("draw-architecture")

# 提示词模板路径
PROMPT_FILE = Path(__file__).parent / "draw_architecture_prompt.md"


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


def generate_drawio_xml(architecture_description: str, diagram_name: str = "架构图") -> str:
    """生成draw.io XML格式的架构图"""
    
    # 基础XML模板
    xml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{timestamp}" agent="MCP Draw Architecture Server" version="24.7.17">
  <diagram name="{diagram_name}" id="{diagram_id}">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- 架构图内容将在这里生成 -->
        {content}
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    # 这里应该根据architecture_description生成具体的图形元素
    # 为了演示，我们创建一个简单的示例
    import time
    import uuid
    
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    diagram_id = str(uuid.uuid4())
    
    # 简单的示例内容
    content = '''
        <!-- 标题 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="400" y="50" width="200" height="30" as="geometry" />
        </mxCell>
        
        <!-- 客户端层 -->
        <mxCell id="client-layer" value="客户端层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="120" width="800" height="60" as="geometry" />
        </mxCell>
        
        <!-- 接入层 -->
        <mxCell id="gateway-layer" value="接入层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="220" width="800" height="60" as="geometry" />
        </mxCell>
        
        <!-- 业务层 -->
        <mxCell id="business-layer" value="业务层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="320" width="800" height="60" as="geometry" />
        </mxCell>
        
        <!-- 数据层 -->
        <mxCell id="data-layer" value="数据层" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="420" width="800" height="60" as="geometry" />
        </mxCell>
    '''.format(title=diagram_name)
    
    return xml_template.format(
        timestamp=timestamp,
        diagram_name=diagram_name,
        diagram_id=diagram_id,
        content=content
    )


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri="prompt://draw-architecture",
            name="Draw.io架构图绘制提示词",
            description="专业的draw.io架构图绘制提示词模板",
            mimeType="text/markdown"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    if uri == "prompt://draw-architecture":
        return load_prompt_template()
    else:
        raise ValueError(f"未知资源: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="generate_architecture_diagram",
            description="根据架构描述生成draw.io格式的架构图",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "架构描述，包括系统组件、层次结构、技术栈等信息"
                    },
                    "diagram_name": {
                        "type": "string",
                        "description": "图表名称",
                        "default": "系统架构图"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出文件路径（可选）"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="get_architecture_prompt",
            description="获取draw.io架构图绘制的专业提示词",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="validate_drawio_file",
            description="验证draw.io文件格式是否正确",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要验证的draw.io文件路径"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    
    if name == "generate_architecture_diagram":
        description = arguments.get("description", "")
        diagram_name = arguments.get("diagram_name", "系统架构图")
        output_file = arguments.get("output_file")
        
        if not description:
            return [TextContent(
                type="text",
                text="错误：请提供架构描述"
            )]
        
        # 生成draw.io XML
        xml_content = generate_drawio_xml(description, diagram_name)
        
        # 如果指定了输出文件，保存到文件
        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                
                return [TextContent(
                    type="text",
                    text=f"架构图已生成并保存到: {output_file}\n\n{xml_content}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"保存文件失败: {e}\n\n生成的XML内容:\n{xml_content}"
                )]
        else:
            return [TextContent(
                type="text",
                text=f"架构图XML内容:\n\n{xml_content}"
            )]
    
    elif name == "get_architecture_prompt":
        prompt_content = load_prompt_template()
        if prompt_content:
            return [TextContent(
                type="text",
                text=prompt_content
            )]
        else:
            return [TextContent(
                type="text",
                text="错误：无法加载提示词模板"
            )]
    
    elif name == "validate_drawio_file":
        file_path = arguments.get("file_path", "")
        
        if not file_path:
            return [TextContent(
                type="text",
                text="错误：请提供文件路径"
            )]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本验证
            validation_results = []
            
            # 检查XML声明
            if not content.startswith('<?xml'):
                validation_results.append("❌ 缺少XML声明")
            else:
                validation_results.append("✅ XML声明正确")
            
            # 检查mxfile根元素
            if '<mxfile' not in content:
                validation_results.append("❌ 缺少mxfile根元素")
            else:
                validation_results.append("✅ mxfile根元素存在")
            
            # 检查diagram元素
            if '<diagram' not in content:
                validation_results.append("❌ 缺少diagram元素")
            else:
                validation_results.append("✅ diagram元素存在")
            
            # 检查mxGraphModel
            if '<mxGraphModel' not in content:
                validation_results.append("❌ 缺少mxGraphModel元素")
            else:
                validation_results.append("✅ mxGraphModel元素存在")
            
            # 检查未转义的HTML标签
            import re
            unescaped_tags = re.findall(r'value="[^"]*<(?!br/&gt;)[^>]*>', content)
            if unescaped_tags:
                validation_results.append(f"❌ 发现未转义的HTML标签: {len(unescaped_tags)}个")
            else:
                validation_results.append("✅ 没有发现未转义的HTML标签")
            
            result_text = f"文件验证结果 ({file_path}):\n\n" + "\n".join(validation_results)
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text=f"错误：文件不存在 - {file_path}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"验证失败: {e}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"未知工具: {name}"
        )]


async def main():
    """主函数"""
    # 运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="draw-architecture",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())