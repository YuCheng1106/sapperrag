#SapperRAG API 调用指南
## 目录
1. [文件转换（File Conversion）](#1.-文件转换（File Conversion）)
2. [读取（Reading）](#2.-读取（Reading）)
3. [切片（Chunking）](#3.-切片（Chunking）)
4. [嵌入（Embedding）](#4.-嵌入（Embedding）)
5. [索引（Indexing）](#5.-索引（Indexing）)
6. [获取上下文（Building Context）](#6.-获取上下文（Building-Context）)
7. [获取回答（Getting Answers）](#7.-获取回答（Getting-Answers）)

### 1. 文件转换（File Conversion）
####使用类：ConvertToolFactory
**1.1 调用方式**
```python
from sapperrag import ConvertToolFactory

# 创建一个转换工具工厂实例
factory = ConvertToolFactory()

# 转换文件到 Markdown 格式
markdown_content = factory.convert_file("D:/workplace/sapperrag/input/上饶市科技局需国家层面协调事项的报告.docx")

# 打印转换后的 Markdown 内容
print(markdown_content)
```
**1.2 方法说明**
- **方法**: `方法: convert_file(file_path: str) -> str`
  - **参数**:
    - `file_path`（字符串类型）：要转换的文件路径。
  - **返回值**：返回转换后的文件内容，以 Markdown 格式表示的字符串。

**1.3 输入输出**
- **输入**：文件夹路径（例如：`"D:/workplace/sapperrag/input/上饶市科技局需国家层面协调事项的报告.docx"`）
- **输出**：转换后的 Markdown 内容，以字符串形式返回。

### 2. 读取（Reading）
####使用类：DocumentReader
**2.1 调用方式**
```python
from sapperrag import DocumentReader

# 创建一个读取器实例
local_file_reader = DocumentReader()

# 读取文件夹中的文档
read_result = local_file_reader.read(dir_path="../input")

# 保存读取结果
local_file_reader.save("../output")
```
**2.2 方法说明**
- **方法**: `read(dir_path: str) -> list[Document]`
  - **参数**:
    - `dir_path`（字符串类型）：要读取的文件夹路径。
  - **返回值**：返回一个包含读取到的文档对象的列表。
- **方法**: `save(save_path: str)`
  - **参数**:
    - `save_path`（字符串类型）：保存读取结果的文件路径。
  - **返回值**：无返回值，保存结果到指定路径。

**2.3 输入输出**
- **输入**：文件夹路径（例如：`"../input"`）
- **输出**：读取到的文档对象列表，并将结果保存到指定的输出路径。

###3. 切片（Chunking）
####使用类：TextFileChunker
**3.1 调用方式**
```python
from sapperrag import TextFileChunker

# 创建一个文本文件切片器实例
text_file_chunker = TextFileChunker()

# 对读取的结果进行切片
chunk_result = text_file_chunker.chunk(read_result)

# 保存切片结果
text_file_chunker.save("../output")
```
**3.2 方法说明**
- **方法**: `chunk(read_result: list[Document]) -> List[TextChunk]`
  - **参数**:
    - `read_result`：包含文档对象的列表（读取器的输出）。
  - **返回值**：返回一个包含文本切片对象的列表。
- **方法**: `save(save_path: str)`
  - **参数**:
    - `save_path`：保存切片结果的文件路径。
  - **返回值**：无返回值，保存结果到指定路径。

**3.3 输入输出**
- **输入**：包含文档对象的列表（例如：`read_result`）
- **输出**：文本切片对象列表，并将结果保存到指定的输出路径。

###4. 嵌入（Embedding）
####使用类：ChunkEmbedder 和 Embedding Model
**4.1 调用方式**
```python
from sapperrag import ChunkEmbedder
from sapperrag.embedding import LocalModelEmbedding

# 创建嵌入模型实例
embeder = LocalModelEmbedding("D:\workplace\agentdy\app\common\RAGModuleBase\embedding\model")

# 创建嵌入器实例
chunk_embedder = ChunkEmbedder(embeder)

# 对切片结果进行嵌入
embed_result = chunk_embedder.embed(chunk_result)

# 保存嵌入结果
chunk_embedder.save("../output")
```
**4.2 方法说明**
- **方法**: `embed(chunk_result: List[TextChunk]) -> list`
  - **参数**:
    - `chunk_result`：包含文本切片对象的列表（切片器的输出）。
  - **返回值**：返回一个嵌入向量的列表。
- **方法**: `save(save_path: str)`
  - **参数**:
    - `save_path`：保存嵌入结果的文件路径。
  - **返回值**：无返回值，保存结果到指定路径。

**4.3 输入输出**
- **输入**：文本切片对象列表（例如：`chunk_result`）
- **输出**：嵌入向量列表，并将结果保存到指定的输出路径。
###5. 索引（Indexing）
**5.1 调用方式**
```python
from sapperrag import run_indexer
# 运行索引器
run_indexer("../input", "../output", "text")
```
**5.2 方法说明**
- **方法**: `run_indexer(input_path: str, output_path: str, data_type: str)`
  - **参数**:
    - `input_path`（字符串类型）：要进行索引的数据输入路径。
    - `output_path`（字符串类型）：保存索引结果的输出路径。
    - `data_type`（字符串类型）：数据类型（例如："text", "graph"）。
  - **返回值**：无返回值，直接进行索引操作。

**5.3 输入输出**
- **输入**：数据输入路径，数据输出路径，数据类型
- **输出**：索引成功后，结果保存在指定的输出路径。

###6. 获取上下文（Building Context）
####使用类：TextSearchContext

**6.1 调用方式**
```python
from sapperrag.embedding import OpenAIEmbedding
from sapperrag.retriver import TextSearchContext

# 创建一个嵌入模型实例
embeder = OpenAIEmbedding(openai_key, base_url, "text-embedding-3-small")

# 创建上下文构建器实例
context_builder = TextSearchContext(dir_path="../output1", text_embedder=embeder)

# 构建查询的上下文
query = "高新技术企业和科技型中小企业快速增长"
context = context_builder.build_context(query)
```
**6.2 方法说明**
- **方法**: `build_context(query: str) -> str`
  - **参数**:
    - `query`（字符串类型）：用于构建上下文的查询语句。
  - **返回值**：返回与查询相关的上下文内容，通常是一个文本字符串。

**6.3 输入输出**
- **输入**：查询语句（例如：`"高新技术企业和科技型中小企业快速增长"`）
- **输出**：与查询相关的上下文文本。

###7. 获取回答（Getting Answers）
####使用类：TextSearch

**7.1 调用方式**
```python
from sapperrag.llm.oai import ChatOpenAI
from sapperrag.retriver import TextSearch

# 创建聊天模型实例
chatgpt = ChatOpenAI(openai_key, base_url)

# 创建搜索引擎实例
search_engine = TextSearch(context_builder, chatgpt)

# 执行搜索操作
results = search_engine.search(query)
```
**7.2 方法说明**
- **方法**: `search(query: str) -> list`
  - **参数**:
    - `query`（字符串类型）：用于搜索的查询语句。
  - **返回值**：返回与查询相关的搜索结果列表。

**7.3 输入输出**
- **输入**：查询语句（例如：`"高新技术企业和科技型中小企业快速增长"`）
- **输出**：与查询相关的搜索结果列表。

