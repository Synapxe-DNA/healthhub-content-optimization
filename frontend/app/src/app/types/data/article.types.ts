

export enum ArticleStatus {
    Default="",
    Combined="COMBINED",
    Ignored="IGNORED"
}


export interface Article {
    id: string,
    title: string,
    description: string,
    pr_name: string,
    content_category: string,
    url: string,
    data_modified: string,
    status: ArticleStatus,
    keywords: string[],
    cover_image_url: string,
    engagement_rate: number,
    number_of_views: number
}
