import requests
import re
from xml.etree import ElementTree as ET

import re

def extract_paper_info(reference):
    """
    从参考文献中提取论文信息
    :param reference: 参考文献（字符串）
    :return: 提取的论文信息（字典）
    """
    # 正则表达式匹配作者部分
    authors_match = re.match(r"^(.*?)\s*\.", reference)
    if not authors_match:
        return None
    
    # 提取作者
    authors_part = authors_match.group(1).strip()
    authors = [author.strip() for author in re.split(r",\s*|\s+and\s+", authors_part)]
    
    # 提取标题
    title_match = re.search(r"\.\s*(.*?)\.\s*In", reference)
    if not title_match:
        return None
    title = title_match.group(1).strip()
    
    # 提取会议和年份
    conference_match = re.search(r"In\s*(.*?),\s*(\d{4})", reference)
    if not conference_match:
        return None
    conference = conference_match.group(1).strip()
    year = conference_match.group(2).strip()
    
    return {
        "authors": authors,
        "title": title,
        "conference": conference,
        "year": year
    }

def search_arxiv_by_title(title, max_results=1):
    """
    根据论文标题在 arXiv 上搜索论文
    :param title: 论文标题
    :param max_results: 最大返回结果数量
    :return: 返回 arXiv API 的 XML 数据
    """
    url = f"http://export.arxiv.org/api/query?search_query=ti:{title}&start=0&max_results={max_results}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def parse_arxiv_response(xml_data):
    """
    解析 arXiv API 返回的 XML 数据
    :param xml_data: arXiv API 返回的 XML 数据
    :return: 解析后的论文信息（字典）
    """
    root = ET.fromstring(xml_data)
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        paper_info = {
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
            "authors": [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")],
            "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
            "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
            "pdf_link": None
        }
        # 提取 PDF 下载链接
        for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
            if link.attrib.get("title") == "pdf":
                paper_info["pdf_link"] = link.attrib.get("href")
                break
        return paper_info
    return None

def download_paper(pdf_url, save_path):
    """
    下载论文 PDF 文件
    :param pdf_url: PDF 文件的 URL
    :param save_path: 保存路径
    """
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Paper downloaded and saved to {save_path}")
    else:
        print(f"Failed to download paper from {pdf_url}")

def fetch_paper_from_reference(reference):
    """
    根据参考文献在 arXiv 上爬取论文
    :param reference: 参考文献（字符串）
    :return: 论文信息（字典）
    """
    # 提取论文信息
    paper_info = extract_paper_info(reference)
    print(paper_info)
    paper_info["title"] = "End-to-end dense video captioning with masked transformer"
    # print(f"Searching for paper: {paper_info['title']}")
    
    # 在 arXiv 上搜索论文
    xml_data = search_arxiv_by_title(paper_info["title"])
    if xml_data:
        arxiv_paper_info = parse_arxiv_response(xml_data)
        if arxiv_paper_info:
            print(f"Found paper: {arxiv_paper_info['title']}")
            return arxiv_paper_info
        else:
            print("No matching paper found in arXiv.")
    else:
        print("Failed to retrieve data from arXiv.")
    return None

if __name__ == "__main__":
    # 示例参考文献
    reference = "Zhou, L., Zhou, Y., Corso, J. J., Socher, R., and Xiong, C. End-to-end dense video captioning with masked transformer. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2018."

    # 根据参考文献爬取论文
    paper_info = fetch_paper_from_reference(reference)
    if paper_info:
        print(f"Title: {paper_info['title']}")
        print(f"Authors: {', '.join(paper_info['authors'])}")
        print(f"Published: {paper_info['published']}")
        print(f"PDF Link: {paper_info['pdf_link']}")
        
        # 下载论文 PDF
        if paper_info["pdf_link"]:
            download_paper(paper_info["pdf_link"], f"{paper_info['title'][:50]}.pdf")
        print("-" * 60)