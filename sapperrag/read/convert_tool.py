import os
import tempfile
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from marker.convert import convert_single_pdf


# 定义抽象转换策略类
class ConversionStrategy:
    def convert(self, file_path):
        raise NotImplementedError("Subclasses should implement this method.")


# PDF 转换策略
class PdfToMd(ConversionStrategy):
    def convert(self, file_path):
        full_text, images, out_meta = convert_single_pdf(file_path, model_state=None)  # 假设不需要 model_state
        markdown_text = f"# PDF Content\n\n{full_text}"
        return markdown_text


# DOC/DOCX 转换策略
class DocToMd(ConversionStrategy):
    def convert(self, file_path):
        output_pdf_path = self._convert_to_pdf(file_path)
        full_text, images, out_meta = convert_single_pdf(output_pdf_path, model_state=None)
        os.remove(output_pdf_path)  # 清理中间生成的 PDF 文件
        markdown_text = f"# DOC Content\n\n{full_text}"
        return markdown_text

    def _convert_to_pdf(self, file_path):
        output_dir = tempfile.mkdtemp()
        command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, file_path]
        subprocess.run(command, check=True)
        return os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + ".pdf")


# PPT/PPTX 转换策略
class PptToMd(ConversionStrategy):
    def convert(self, file_path):
        output_pdf_path = self._convert_to_pdf(file_path)
        full_text, images, out_meta = convert_single_pdf(output_pdf_path, model_state=None)
        os.remove(output_pdf_path)  # 清理中间生成的 PDF 文件
        markdown_text = f"# PPT Content\n\n{full_text}"
        return markdown_text

    def _convert_to_pdf(self, file_path):
        output_dir = tempfile.mkdtemp()
        command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, file_path]
        subprocess.run(command, check=True)
        return os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + ".pdf")


# Excel 转换策略
class ExcelToMd(ConversionStrategy):
    def convert(self, file_path):
        df = pd.read_excel(file_path)
        markdown_text = df.to_markdown(index=False)
        return f"# Excel Content\n\n{markdown_text}"


# CSV 转换策略
class CsvToMd(ConversionStrategy):
    def convert(self, file_path):
        df = pd.read_csv(file_path)
        markdown_text = df.to_markdown(index=False)
        return f"# CSV Content\n\n{markdown_text}"


# HTML 转换策略
class HtmlToMd(ConversionStrategy):
    def convert(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        markdown_text = self._html_to_markdown(soup)
        return f"# HTML Content\n\n{markdown_text}"

    def _html_to_markdown(self, soup):
        # 使用 BeautifulSoup 将 HTML 转换为 Markdown 格式
        markdown_lines = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'tr', 'th', 'td']):
            if element.name in ['h1', 'h2', 'h3']:
                markdown_lines.append(f"{'#' * (int(element.name[1]))} {element.get_text()}")
            elif element.name == 'p':
                markdown_lines.append(element.get_text())
            elif element.name == 'ul':
                markdown_lines.extend([f"- {li.get_text()}" for li in element.find_all('li')])
            elif element.name == 'ol':
                markdown_lines.extend([f"1. {li.get_text()}" for li in element.find_all('li')])
            elif element.name == 'table':
                table_md = self._convert_table_to_markdown(element)
                markdown_lines.append(table_md)
        return "\n\n".join(markdown_lines)

    def _convert_table_to_markdown(self, table):
        # 转换 HTML 表格为 Markdown 表格
        headers = [th.get_text() for th in table.find_all('th')]
        rows = [[td.get_text() for td in row.find_all('td')] for row in table.find_all('tr')]
        df = pd.DataFrame(rows, columns=headers if headers else None)
        return df.to_markdown(index=False)


# ConvertToolFactory 工厂类
class ConvertToolFactory:
    def __init__(self):
        self.strategies = {
            "pdf": PdfToMd(),
            "doc": DocToMd(),
            "docx": DocToMd(),
            "ppt": PptToMd(),
            "pptx": PptToMd(),
            "xls": ExcelToMd(),
            "xlsx": ExcelToMd(),
            "csv": CsvToMd(),
            "html": HtmlToMd(),
        }

    def convert_file(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower().strip('.')
        strategy = self.strategies.get(file_extension)
        if not strategy:
            raise ValueError(f"Unsupported file format: {file_extension}")
        return strategy.convert(file_path)


# from sapperrag import ConvertToolFactory
# factory = ConvertToolFactory()
# markdown_content = factory.convert_file("D:\workplace\sapperrag\input\上饶市科技局需国家层面协调事项的报告.docx")
# print(markdown_content)
