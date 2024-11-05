import gradio as gr
import os
from main import main
from logger import LOG
import tempfile

def format_to_markdown(text: str) -> str:
    """
    将用户输入转换为ChatPPT标准的Markdown格式
    """
    lines = text.strip().split('\n')
    formatted_lines = []
    
    # 如果第一行不是标题，添加一个默认标题
    if not lines[0].startswith('# '):
        formatted_lines.append('# 演示文稿')
    
    for line in lines:
        line = line.strip()
        if line:
            # 如果是新的主题，添加为二级标题
            if not line.startswith(('#', '-', '!')):
                formatted_lines.append(f'## {line}')
            # 如果不是以'-'开头的内容，将其转换为要点
            elif not line.startswith(('#', '-', '!')):
                formatted_lines.append(f'- {line}')
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def generate_ppt(text: str, state=None) -> tuple:
    """
    处理用户输入并生成PPT
    """
    try:
        # 格式化用户输入为Markdown
        formatted_text = format_to_markdown(text)
        
        # 创建临时文件来存储markdown内容
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(formatted_text)
            temp_file.flush()
            input_file = temp_file.name
        
        # 生成PPT
        main(input_file)
        
        # 删除临时文件
        os.unlink(input_file)
        
        # 获取生成的PPT文件路径
        output_files = [f for f in os.listdir('outputs') if f.endswith('.pptx')]
        if output_files:
            ppt_path = os.path.join('outputs', output_files[-1])
            return [(text, "user"), (f"PPT已生成: {ppt_path}", "assistant")], state
        else:
            return [(text, "user"), ("PPT生成失败", "assistant")], state
            
    except Exception as e:
        LOG.error(f"生成PPT时发生错误: {str(e)}")
        return [(text, "user"), (f"发生错误: {str(e)}", "assistant")], state

def create_interface():
    """
    创建Gradio界面
    """
    with gr.Blocks(title="ChatPPT") as interface:
        chatbot = gr.Chatbot(
            label="对话历史",
            height=400
        )
        
        with gr.Row():
            txt = gr.Textbox(
                label="输入内容",
                placeholder="请输入您要转换为PPT的内容...",
                lines=5
            )
        
        with gr.Row():
            submit_btn = gr.Button("生成PPT")
            clear_btn = gr.Button("清除")
        
        state = gr.State()
        
        # 绑定事件
        submit_btn.click(
            generate_ppt,
            inputs=[txt, state],
            outputs=[chatbot, state]
        )
        
        clear_btn.click(
            lambda: (None, None),
            outputs=[chatbot, txt]
        )
        
        # 添加使用说明
        gr.Markdown("""
        ### 使用说明
        1. 在输入框中输入您要转换为PPT的内容
        2. 系统会自动将内容组织为合适的PPT格式
        3. 点击"生成PPT"按钮生成演示文稿
        4. 生成的PPT文件将保存在outputs目录下
        
        ### 输入格式示例
        ```
        人工智能简介
        
        什么是人工智能
        - 人工智能是计算机科学的一个分支
        - 致力于创造能模拟人类智能的系统
        
        人工智能应用
        - 机器学习
        - 自然语言处理
        - 计算机视觉
        ```
        """)
    
    return interface

if __name__ == "__main__":
    # 确保输出目录存在
    os.makedirs('outputs', exist_ok=True)
    
    # 启动Gradio界面
    interface = create_interface()
    interface.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860
    )