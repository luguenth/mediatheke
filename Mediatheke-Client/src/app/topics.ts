import { IVideoRow } from "./interfaces";

export enum options_type {
    recommended = 'recommended',
    topic = 'topic',
    series = 'series',
    last_seen = 'last_seen',
}

export const home_topics: IVideoRow[] = [
    {
        title: 'Empfohlen von der Community',
        description: 'Jedes Mitglied der Community kann Videos empfehlen, die dann hier angezeigt werden.',
        options: {
            type: options_type.recommended,
            payload: undefined,
            skip: 0,
            limit: 10,
            random_order: true,
        }
    },
    {
        title: 'Sportschau FIFA WM 2026',
        description: 'Alle Highlights, Analysen und Hintergründe zur Fußball-Weltmeisterschaft 2026.',
        options: {
            type: options_type.topic,
            payload: 'Sportschau FIFA WM 2026',
            skip: 0,
            limit: 10,
            random_order: true,
        }
    },
    {
        title: 'Asbest',
        description: 'In Babylon Berlin wird die Geschichte des Kriminalkommissars Gereon Rath erzählt, der im Berlin der 1920er Jahre ermittelt.',
        options: {
            type: options_type.topic,
            payload: 'Asbest',
            skip: 0,
            limit: 10,
            random_order: false,
        }
    },
    {
        title: 'Bereit für einen Serienmarathon?',
        description: 'Hier findest du alle Serien, die wir erfasst haben.',
        options: {
            type: options_type.series,
            payload: undefined,
            skip: 0,
            limit: 10,
            random_order: true,
        }
    },
    {
        title: 'Sportschau Olympia 2026',
        description: 'Berichte, Interviews und Analysen rund um die Olympischen Winterspiele 2026.',
        options: {
            type: options_type.topic,
            payload: 'Sportschau Olympia 2026',
            skip: 0,
            limit: 10,
            random_order: true,
        }
    },
    {
        title: 'Zuletzt gesehen',
        description: 'Hier findest du die Videos, die du zuletzt gesehen hast.',
        options: {
            type: options_type.last_seen,
            payload: undefined,
            skip: 0,
            limit: 10,
            random_order: false,
        }
    }
];
