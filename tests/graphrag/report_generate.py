import openai
import json
import pandas as pd
import concurrent.futures


class CommunityReportGenerator:
    def __init__(self, api_key, api_base, input_data):
        # 初始化OpenAI API密钥和基础URL
        openai.api_key = api_key
        openai.api_base = api_base
        self.input_data = input_data

        # 定义用于生成报告的提示模板
        self.prompt_template = """
        You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

        # Goal
        Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated attributes. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy attributes.

        # Report Structure

        The report should include the following sections:

        - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
        - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
        - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
        - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
        - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

        Return output as a well-formed JSON-formatted string with the following format:
            {{
                "title": "<report_title>",
                "summary": "<executive_summary>",
                "rating": <impact_severity_rating>,
                "rating_explanation": "<rating_explanation>",
                "findings": [
                    {{
                        "summary": "<insight_1_summary>",
                        "explanation": "<insight_1_explanation>"
                    }},
                    {{
                        "summary": "<insight_2_summary>",
                        "explanation": "<insight_2_explanation>"
                    }}
                ]
            }}

        # Grounding Rules

        Points supported by data should list their data references as follows:

        "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

        Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

        The output results are presented in Chinese.

        For example:
        "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

        where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.

        Do not include information where the supporting evidence for it is not provided.

        # Real Data

        Use the following text for your answer. Do not make anything up in your answer.

        Text:
        {input_text}

        The report should include the following sections:

        - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
        - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
        - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
        - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
        - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

        Return output as a well-formed JSON-formatted string with the following format:
            {{
                "title": "<report_title>",
                "summary": "<executive_summary>",
                "rating": <impact_severity_rating>,
                "rating_explanation": "<rating_explanation>",
                "findings": [
                    {{
                        "summary": "<insight_1_summary>",
                        "explanation": "<insight_1_explanation>"
                    }},
                    {{
                        "summary": "<insight_2_summary>",
                        "explanation": "<insight_2_explanation>"
                    }}
                ]
            }}

        # Grounding Rules

        Points supported by data should list their data references as follows:

        "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

        Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

        For example:
        "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

        where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.

        Do not include information where the supporting evidence for it is not provided.

        Output:
        """

    def preprocess_data(self, community_df):
        # 预处理数据，将每个实体的信息格式化为字符串
        input_text = "\n".join([
            f"{row['node_name']} ({row['node_id']}): {json.loads(row['node_details'])['attributes'].get('描述', '无描述')}"
            for _, row in community_df.iterrows()
        ])
        return input_text

    def chat_response(self, prompt):
        # 调用OpenAI的ChatCompletion API获取响应
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response['choices'][0]['message']['content']

    def generate_report_for_community(self, community_name, community_df):
        # 为特定社区生成报告
        input_text = self.preprocess_data(community_df)
        prompt = self.prompt_template.format(input_text=input_text)
        response = self.chat_response(prompt=prompt)
        return response

    def generate_reports(self):
        # 生成所有社区的报告
        grouped = self.input_data.groupby('community_name')
        reports = []

        def process_community(community_name, community_df):
            # 处理单个社区
            report = self.generate_report_for_community(community_name, community_df)
            return {"community_name": community_name, "report": report}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 使用多线程并发处理多个社区
            future_to_community = {executor.submit(process_community, name, df): name for name, df in grouped}

            for future in concurrent.futures.as_completed(future_to_community):
                community_name = future_to_community[future]
                try:
                    report = future.result()
                    reports.append(report)
                except Exception as exc:
                    print(f"{community_name} generated an exception: {exc}")

        reports_df = pd.DataFrame(reports)
        return reports_df

    def save_reports_to_csv(self, reports_df, file_name):
        # 将生成的报告保存为CSV文件
        reports_df.to_csv(file_name, index=False)
