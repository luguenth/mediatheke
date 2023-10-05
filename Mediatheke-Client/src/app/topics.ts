import { IVideoRow } from "./interfaces";

export enum options_type {
    recommended = 'recommended',
    topic = 'topic',
    series = 'series',
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
        title: 'Babylon Berlin',
        description: 'In Babylon Berlin wird die Geschichte des Kriminalkommissars Gereon Rath erzählt, der im Berlin der 1920er Jahre ermittelt.',
        options: {
            type: options_type.topic,
            payload: 'babylon berlin',
            skip: 0,
            limit: 10,
            random_order: true,
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
];
