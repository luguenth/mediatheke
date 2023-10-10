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
        title: 'Auf der Couch',
        description: 'Zwei Menschen mit unterschiedlichen Meinungen wagen "Auf der Couch" eine Annäherung mithilfe des Psychologen Leon Windscheid Kommen sie sich näher?',
        options: {
            type: options_type.topic,
            payload: 'Auf der Couch',
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
            payload: 'Babylon Berlin',
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
    {
        title: 'Mit offenen Karten',
        description: 'In der Sendung Mit offenen Karten werden geopolitische Themen aufgegriffen und erklärt.',
        options: {
            type: options_type.topic,
            payload: 'Mit offenen Karten - Geopolitisches Magazin',
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
