import os
import re
from PyPDF2 import PdfReader

def extract_references_from_pdf(pdf_path, output_folder='txtfile'):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 读取 PDF 文件
    reader = PdfReader(pdf_path)
    text = ""
    
    # 合并所有页面文本
    for page in reader.pages:
        text += page.extract_text()
    
    # 获取PDF文件名（不含扩展名）作为TXT文件名
    pdf_filename_without_ext = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_filename = f"{pdf_filename_without_ext}.txt"
    
    # 创建完整的TXT文件路径
    txt_filepath = os.path.join(output_folder, txt_filename)
    
    # 将提取的内容写入TXT文件
    with open(txt_filepath, 'w', encoding='utf-8') as file:
        file.write(text)
    
    # 定位 "References" 部分
    references_start = re.search(r"(References|Bibliography)", text, re.IGNORECASE)
    if not references_start:
        return "未找到参考文献部分"
    
    # 提取参考文献部分
    references_text = text[references_start.start():]

    # 返回TXT文件路径
    return references_text, txt_filepath

# 示例调用
if __name__ == '__main__':
    pdf_path = 'Timesformers.pdf'
    result, path = extract_references_from_pdf(pdf_path)
    print(result)  # 打印返回的TXT文件路径
    




