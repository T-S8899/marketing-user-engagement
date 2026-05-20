export const RAW_TABLES = [
  {
    id: "market_comments",
    label: "Market Comments",
    path: "../../../data/processed/market_comments.csv",
    downloadPath: "../data/processed/market_comments.csv",
    description: "Canonical normalized comments and reviews. This is the source of truth for downstream analysis.",
    dictionary: [
      ["record_id", "Stable generated identifier for the normalized record."],
      ["raw_record_hash", "Hash of the original raw JSON record."],
      ["platform", "Source platform such as TikTok, Instagram, X, or App Store."],
      ["text", "Original comment or review text, including Arabic or English."],
      ["raw_file_path", "Local raw JSON file reference when available."]
    ]
  },
  {
    id: "posts",
    label: "Posts",
    path: "../../../data/processed/posts.csv",
    downloadPath: "../data/processed/posts.csv",
    description: "Post-level references extracted during normalization when a comment can be linked to a post, video, tweet, or source item.",
    dictionary: [
      ["post_record_id", "Stable generated post-level identifier."],
      ["post_id", "Platform post, video, tweet, or thread identifier when available."],
      ["post_url", "Source post URL when available."],
      ["raw_record_hash", "Hash linking back to the raw record."]
    ]
  },
  {
    id: "sources",
    label: "Sources",
    path: "../../../data/processed/sources.csv",
    downloadPath: "../data/processed/sources.csv",
    description: "Source/account/app references extracted from normalized records.",
    dictionary: [
      ["source_record_id", "Stable generated source-level identifier."],
      ["source_account", "Account, app, or source name when available."],
      ["source_url", "Source URL when available."],
      ["brand_or_competitor", "Configured brand grouping when available."]
    ]
  },
  {
    id: "scrape_runs",
    label: "Scrape Runs",
    path: "../../../data/processed/scrape_runs.csv",
    downloadPath: "../data/processed/scrape_runs.csv",
    description: "Run-level Apify scrape log with actor, input, dataset, status, and error fields.",
    dictionary: [
      ["run_id", "Local scrape run identifier."],
      ["actor_id", "Apify actor ID loaded from config."],
      ["dataset_id", "Apify dataset ID returned by the run."],
      ["status", "Run status or failure status."],
      ["error_message", "Captured error details when a run fails."]
    ]
  },
  {
    id: "raw_records_log",
    label: "Raw Records Log",
    path: "../../../data/processed/raw_records_log.csv",
    downloadPath: "../data/processed/raw_records_log.csv",
    description: "Record-level trace log linking raw dataset items to saved raw files.",
    dictionary: [
      ["run_id", "Local scrape run identifier."],
      ["record_index", "Index of the record in the raw file."],
      ["record_key", "Best available raw record key."],
      ["raw_file_path", "Local raw JSON file reference."]
    ]
  },
  {
    id: "normalization_errors",
    label: "Normalization Errors",
    path: "../../../data/processed/normalization_errors.csv",
    downloadPath: "../data/processed/normalization_errors.csv",
    description: "Errors captured while converting raw JSON records into normalized processed CSVs.",
    dictionary: [
      ["error_id", "Stable generated error identifier."],
      ["raw_record_index", "Index of the raw record that failed normalization."],
      ["error_message", "Error captured without stopping the normalization run."],
      ["raw_record_hash", "Hash of the affected raw record when available."]
    ]
  },
  {
    id: "comment_analysis",
    label: "Comment Analysis",
    path: "../../../data/analysis/comment_analysis.csv",
    downloadPath: "../data/analysis/comment_analysis.csv",
    description: "Per-comment analysis output with sentiment, category, keywords, urgency, reasons, and recommendations.",
    dictionary: [
      ["record_id", "Normalized record identifier."],
      ["sentiment_label", "Prepared sentiment label from the analysis layer."],
      ["concern_category_label", "Prepared concern category label from analysis/config."],
      ["keywords", "Extracted keywords from the analysis layer."],
      ["recommended_action", "Prepared recommendation from the analysis layer."]
    ]
  },
  {
    id: "concern_category_summary",
    label: "Concern Category Summary",
    path: "../../../data/analysis/concern_category_summary.csv",
    downloadPath: "../data/analysis/concern_category_summary.csv",
    description: "Concern category rollup with counts, sentiment split, urgency count, and example text.",
    dictionary: [
      ["label", "Concern category label."],
      ["comments_count", "Number of comments in the category."],
      ["share_of_total", "Share of analyzed comments."],
      ["urgent_count", "Number of urgent comments in the category."]
    ]
  },
  {
    id: "sentiment_summary",
    label: "Sentiment Summary",
    path: "../../../data/analysis/sentiment_summary.csv",
    downloadPath: "../data/analysis/sentiment_summary.csv",
    description: "Sentiment rollup across analyzed comments.",
    dictionary: [
      ["label", "Sentiment label."],
      ["comments_count", "Number of comments for the sentiment."],
      ["share_of_total", "Share of analyzed comments."]
    ]
  },
  {
    id: "platform_summary",
    label: "Platform Summary",
    path: "../../../data/analysis/platform_summary.csv",
    downloadPath: "../data/analysis/platform_summary.csv",
    description: "Platform-level summary with sentiment and urgency counts.",
    dictionary: [
      ["label", "Platform name."],
      ["comments_count", "Number of comments on the platform."],
      ["positive_count", "Positive comment count."],
      ["negative_count", "Negative comment count."]
    ]
  },
  {
    id: "brand_competitor_summary",
    label: "Brand Competitor Summary",
    path: "../../../data/analysis/brand_competitor_summary.csv",
    downloadPath: "../data/analysis/brand_competitor_summary.csv",
    description: "Brand or competitor grouping summary with sentiment and urgency counts.",
    dictionary: [
      ["label", "Brand or competitor group."],
      ["comments_count", "Number of comments for the group."],
      ["positive_count", "Positive comment count."],
      ["negative_count", "Negative comment count."]
    ]
  },
  {
    id: "keyword_summary",
    label: "Keyword Summary",
    path: "../../../data/analysis/keyword_summary.csv",
    downloadPath: "../data/analysis/keyword_summary.csv",
    description: "Keyword frequency rollup with platform, brand, sentiment, and urgency context.",
    dictionary: [
      ["keyword", "Extracted keyword."],
      ["comments_count", "Number of comments containing the keyword."],
      ["platforms", "Platforms where the keyword appears."],
      ["brands", "Brand groups where the keyword appears."]
    ]
  },
  {
    id: "emerging_concerns",
    label: "Emerging Concerns",
    path: "../../../data/analysis/emerging_concerns.csv",
    downloadPath: "../data/analysis/emerging_concerns.csv",
    description: "Recent concern growth candidates produced by the analysis layer.",
    dictionary: [
      ["concern_category_label", "Concern category or emerging signal."],
      ["comments_count", "Recent count or growth count."],
      ["reason", "Explainable reason from analysis output."],
      ["recommended_action", "Suggested action from analysis output."]
    ]
  },
  {
    id: "urgent_comments",
    label: "Urgent Comments",
    path: "../../../data/analysis/urgent_comments.csv",
    downloadPath: "../data/analysis/urgent_comments.csv",
    description: "Subset of comments flagged as urgent by the analysis layer.",
    dictionary: [
      ["record_id", "Normalized record identifier."],
      ["urgency_flag", "Urgency flag from analysis output."],
      ["urgency_reason", "Explainable urgency reason."],
      ["text", "Original comment text."]
    ]
  },
  {
    id: "marketing_opportunities",
    label: "Marketing Opportunities",
    path: "../../../data/analysis/marketing_opportunities.csv",
    downloadPath: "../data/analysis/marketing_opportunities.csv",
    description: "Prepared campaign, positioning, and messaging opportunities from analysis outputs.",
    dictionary: [
      ["type", "Opportunity type."],
      ["keyword", "Theme or keyword behind the opportunity."],
      ["recommended_action", "Suggested marketing action."],
      ["example_text", "Trace example when available."]
    ]
  },
  {
    id: "content_ideas",
    label: "Content Ideas",
    path: "../../../data/analysis/content_ideas.csv",
    downloadPath: "../data/analysis/content_ideas.csv",
    description: "Prepared FAQ, explainer, response, or social content opportunities from analysis outputs.",
    dictionary: [
      ["concern_category_label", "Concern or objection theme."],
      ["reason", "Why this content may help."],
      ["recommended_action", "Suggested content angle."],
      ["example_text", "Trace example when available."]
    ]
  },
  {
    id: "escalation_items",
    label: "Escalation Items",
    path: "../../../data/analysis/escalation_items.csv",
    downloadPath: "../data/analysis/escalation_items.csv",
    description: "Urgent or high-priority items formatted for follow-up.",
    dictionary: [
      ["record_id", "Normalized record identifier."],
      ["concern_category_label", "Concern category."],
      ["urgency_reason", "Explainable urgency reason."],
      ["recommended_action", "Suggested next action."]
    ]
  }
];

export function rawTableById(id) {
  return RAW_TABLES.find((table) => table.id === id) || RAW_TABLES[0];
}
