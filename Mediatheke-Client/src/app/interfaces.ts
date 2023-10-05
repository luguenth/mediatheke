// Common Interfaces


export interface IUser {
    id: number;
    email: string;
    username: string;
    password: string;
}

export interface IVideo {
    channel: string;
    topic: string;
    title: string;
    date: string;
    time: string;
    duration: number;
    size_MB: string;
    description: string;
    url_video: string;
    url_video_hd: string;
    url_video_low: string;
    url_video_descriptive_audio: string;
    url_video_hd_descriptive_audio: string;
    url_video_low_descriptive_audio: string;
    id: number;
    url_website: string;
    thumbnail: string;
    url_subtitle: string;
    episode_number: number;
    season_number: number;
    series_name: string;
}

export interface IToken {
    access_token: string;
    token_type: string;
}

export interface ITokenResponse {
    access_token: string;
    token_type: string;
}

export interface ITokenPayload {
    sub: string;
    exp: number;
    context: {
        username: string;
        role: string;
    };
}

export interface IVideoLocalStorage {
    id: number;
    position: number;
    lastPlayedTimestamp: number;
}

export interface IVideoThumbnailUrl {
    media_item_id: number;
    url: string;
}

export type IMediaItemSearchResponse = IVideo[];

export interface IVideoOptions {
    type: string;
    payload: string | undefined;
    skip: number;
    limit: number;
    random_order: boolean;
}

export interface IVideoRow {
    title: string;
    description: string;
    options: IVideoOptions;
}