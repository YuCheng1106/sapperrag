import json
import pandas as pd
import concurrent.futures
from ....index.graph.promt.report_generate import REPORT_GENERATE
from ....llm.base import BaseLLM


class CommunityReportGenerator:
    def __init__(self, llm: BaseLLM, input_data):
        self.input_data = input_data
        self.llm = llm
        # 定义用于生成报告的提示模板
        self.prompt_template = REPORT_GENERATE

    def preprocess_data(self, community):
        # 预处理数据，将每个实体的信息格式化为字符串
        input_text = f"{community.title} ({community.id}): {community.full_content}"

        return input_text

    def chat_response(self, prompt):
        # 调用OpenAI的ChatCompletion API获取响应
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = self.llm.generate(messages)

        return response

    def generate_report_for_community(self, community_name, community_df):
        # 为特定社区生成报告
        input_text = self.preprocess_data(community_df)
        prompt = self.prompt_template.format(input_text=input_text)
        response = self.chat_response(prompt=prompt)
        return response

    def generate_reports(self):
        # 生成所有社区的报告
        grouped = self.input_data
        reports = []

        def process_community(community_name, community_df):
            # 处理单个社区
            report = self.generate_report_for_community(community_name, community_df)
            return report

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 使用多线程并发处理多个社区
            future_to_community = {executor.submit(process_community, df.id, df): ids for ids, df in enumerate(grouped)}

            for future in concurrent.futures.as_completed(future_to_community):
                community_name = future_to_community[future]
                try:
                    report = future.result().replace("json", "").replace("```", "")
                    report_data = json.loads(report)
                    title = report_data['title']
                    rating = report_data['rating']
                    grouped[community_name].full_content = report
                    grouped[community_name].title = title
                    grouped[community_name].rating = rating
                    reports.append(report)
                except Exception as exc:
                    print(f"{community_name} generated an exception: {exc}")

        return grouped

    def save_reports_to_csv(self, reports_df, file_name):
        # 将生成的报告保存为CSV文件
        reports_df.to_csv(file_name, index=False)
