#!/usr/bin/env python3
"""
测试 Draw.io Architecture MCP Server 的基本功能
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

# 导入MCP服务器模块
try:
    from mcp_server import (
        generate_drawio_xml,
        load_prompt_template,
        handle_call_tool,
        handle_list_tools,
        handle_list_resources,
        handle_read_resource
    )
except ImportError:
    print("错误: 无法导入 mcp_server 模块")
    print("请确保在正确的目录中运行此测试脚本")
    exit(1)


async def test_list_tools():
    """测试工具列表功能"""
    print("\n=== 测试工具列表 ===")
    try:
        tools = await handle_list_tools()
        print(f"✅ 成功获取 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        return True
    except Exception as e:
        print(f"❌ 工具列表测试失败: {e}")
        return False


async def test_list_resources():
    """测试资源列表功能"""
    print("\n=== 测试资源列表 ===")
    try:
        resources = await handle_list_resources()
        print(f"✅ 成功获取 {len(resources)} 个资源:")
        for resource in resources:
            print(f"  - {resource.name}: {resource.description}")
        return True
    except Exception as e:
        print(f"❌ 资源列表测试失败: {e}")
        return False


async def test_get_prompt():
    """测试获取提示词功能"""
    print("\n=== 测试获取提示词 ===")
    try:
        result = await handle_call_tool("get_architecture_prompt", {})
        if result and len(result) > 0:
            content = result[0].text
            if len(content) > 100:  # 检查内容是否足够长
                print("✅ 成功获取提示词模板")
                print(f"  提示词长度: {len(content)} 字符")
                print(f"  前100字符: {content[:100]}...")
                return True
            else:
                print("❌ 提示词内容太短")
                return False
        else:
            print("❌ 未获取到提示词内容")
            return False
    except Exception as e:
        print(f"❌ 获取提示词测试失败: {e}")
        return False


async def test_generate_diagram():
    """测试生成架构图功能"""
    print("\n=== 测试生成架构图 ===")
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.drawio', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # 测试参数
        test_args = {
            "description": "简单的三层架构，包括Web前端、应用服务器和数据库",
            "diagram_name": "测试架构图",
            "output_file": tmp_path
        }
        
        result = await handle_call_tool("generate_architecture_diagram", test_args)
        
        if result and len(result) > 0:
            # 检查文件是否创建
            if os.path.exists(tmp_path):
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 基本验证
                if (content.startswith('<?xml') and 
                    '<mxfile' in content and 
                    '<diagram' in content and 
                    '测试架构图' in content):
                    print("✅ 成功生成架构图")
                    print(f"  文件路径: {tmp_path}")
                    print(f"  文件大小: {len(content)} 字符")
                    
                    # 清理临时文件
                    os.unlink(tmp_path)
                    return True
                else:
                    print("❌ 生成的文件格式不正确")
                    print(f"  文件内容前100字符: {content[:100]}")
                    os.unlink(tmp_path)
                    return False
            else:
                print("❌ 文件未创建")
                return False
        else:
            print("❌ 未获取到生成结果")
            return False
            
    except Exception as e:
        print(f"❌ 生成架构图测试失败: {e}")
        return False


async def test_validate_file():
    """测试文件验证功能"""
    print("\n=== 测试文件验证 ===")
    try:
        # 创建一个测试文件
        test_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="test" version="1.0.0">
  <diagram name="测试图" id="test-001">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="test-cell" value="测试单元格" style="rounded=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="120" height="60" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.drawio', delete=False) as tmp_file:
            tmp_file.write(test_content)
            tmp_path = tmp_file.name
        
        # 测试验证功能
        test_args = {"file_path": tmp_path}
        result = await handle_call_tool("validate_drawio_file", test_args)
        
        if result and len(result) > 0:
            validation_result = result[0].text
            if "✅" in validation_result:
                print("✅ 文件验证功能正常")
                print(f"  验证结果: {validation_result.split(':', 1)[0]}")
                
                # 清理临时文件
                os.unlink(tmp_path)
                return True
            else:
                print("❌ 验证结果异常")
                print(f"  验证结果: {validation_result}")
                os.unlink(tmp_path)
                return False
        else:
            print("❌ 未获取到验证结果")
            os.unlink(tmp_path)
            return False
            
    except Exception as e:
        print(f"❌ 文件验证测试失败: {e}")
        return False


async def test_xml_generation():
    """测试XML生成功能"""
    print("\n=== 测试XML生成 ===")
    try:
        xml_content = generate_drawio_xml(
            "测试架构描述", 
            "测试图表"
        )
        
        # 基本验证
        if (xml_content.startswith('<?xml') and 
            '<mxfile' in xml_content and 
            '<diagram' in xml_content and 
            '测试图表' in xml_content and 
            '</mxfile>' in xml_content):
            print("✅ XML生成功能正常")
            print(f"  XML长度: {len(xml_content)} 字符")
            return True
        else:
            print("❌ XML格式不正确")
            print(f"  XML前200字符: {xml_content[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ XML生成测试失败: {e}")
        return False


async def test_prompt_loading():
    """测试提示词加载功能"""
    print("\n=== 测试提示词加载 ===")
    try:
        prompt_content = load_prompt_template()
        
        if prompt_content and len(prompt_content) > 100:
            print("✅ 提示词加载功能正常")
            print(f"  提示词长度: {len(prompt_content)} 字符")
            
            # 检查关键内容
            if "Draw.io" in prompt_content and "架构图" in prompt_content:
                print("  ✅ 包含关键内容")
                return True
            else:
                print("  ❌ 缺少关键内容")
                return False
        else:
            print("❌ 提示词内容为空或太短")
            return False
            
    except Exception as e:
        print(f"❌ 提示词加载测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始测试 Draw.io Architecture MCP Server")
    print("=" * 50)
    
    tests = [
        ("提示词加载", test_prompt_loading),
        ("XML生成", test_xml_generation),
        ("工具列表", test_list_tools),
        ("资源列表", test_list_resources),
        ("获取提示词", test_get_prompt),
        ("生成架构图", test_generate_diagram),
        ("文件验证", test_validate_file),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MCP服务器功能正常")
        return True
    else:
        print(f"⚠️  有 {total - passed} 个测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    # 检查当前目录
    current_dir = Path.cwd()
    if not (current_dir / "mcp_server.py").exists():
        print("错误: 请在包含 mcp_server.py 的目录中运行此测试")
        exit(1)
    
    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)