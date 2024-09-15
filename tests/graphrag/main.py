  from attribute_embedding import AttributeEmbedder
from community_detection import CommunityDetection
from report_generate import CommunityReportGenerator

if __name__ == "__main__":
    api_key = "sk-tQ8RTjMtsRn5Na5H82F0EeBb7e4946198d2e840a48BfBb90"
    api_base = "https://api.rcouyi.com/v1"

    community_detector = CommunityDetection(max_comm_size=10, max_level=1, seed=5)
    vertices, edges = community_detector.load_data("graph.json")
    graph = community_detector.create_graph(vertices, edges)
    df = community_detector.detect_communities(graph)
    community_detector.save_to_csv(df, 'community_levels.csv')

    generator = CommunityReportGenerator(api_key=api_key, input_data=df, api_base=api_base)
    reports_df = generator.generate_reports()
    generator.save_reports_to_csv(reports_df, 'community_reports.csv')

    embedder = AttributeEmbedder(api_key=api_key, api_base=api_base)
    df = embedder.add_attribute_vectors(df)
    community_detector.save_to_csv(df, 'community_levels.csv')
