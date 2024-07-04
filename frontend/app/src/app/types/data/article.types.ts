

export enum ArticleStatus {
    Default="",
    Combined="COMBINED",
    Ignored="IGNORED"
}


export interface Article {
    id: string,
    title: string,
    description: string,
    author: string,
    pillar: string,
    url: string,
    status: ArticleStatus,
    labels: string[],
    cover_image_url: string,
    engagement: number,
    views: number
}
