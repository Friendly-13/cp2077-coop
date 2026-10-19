// @version 1.0
// Read-only metadata report for the q003 quest graphs.
// Reads directly from WolvenKit's mounted game archives and prints a filtered report to the Log.
// This script does not extract, save, export, edit, or package any game resource.

import * as Logger from 'Logger.wscript';

const RESOURCE_PATHS = [
    'base\\quest\\main_quests\\prologue\\q003\\q003.questphase',
    'base\\quest\\main_quests\\prologue\\q003\\q003_royce_deal.questphase',
    'base\\quest\\main_quests\\prologue\\q003\\scenes\\q003_03_deal.scene'
];

const INTERESTING_FIELDS = new Set([
    'debugstring',
    'factname',
    'setexactvalue',
    'value',
    'comparisontype',
    'sceneFile',
    'scenelocation',
    'phaseresource',
    'reward',
    'rewardname',
    'savelock',
    'endgamesave',
    'ignoresavelocks',
    'pointofnoreturn',
    'retryonfailure'
].map(x => x.toLowerCase()));

function prop(obj, name) {
    if (obj === null || obj === undefined || typeof obj !== 'object') return undefined;
    if (Object.prototype.hasOwnProperty.call(obj, name)) return obj[name];
    const target = name.toLowerCase();
    for (const key of Object.keys(obj)) {
        if (key.toLowerCase() === target) return obj[key];
    }
    return undefined;
}

function unwrap(value) {
    let current = value;
    for (let i = 0; i < 5; i++) {
        if (current === null || current === undefined || typeof current !== 'object' || Array.isArray(current)) break;
        let next = prop(current, 'Chunk');
        if (next === undefined) next = prop(current, 'Data');
        if (next === undefined) next = prop(current, '$value');
        if (next === undefined || next === current || typeof next !== 'object') break;
        current = next;
    }
    return current;
}

function compact(value, limit = 320) {
    if (value === null || value === undefined || typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        return value;
    }
    if (Array.isArray(value)) {
        return value.slice(0, 12).map(item => compact(item, limit));
    }
    const typedValue = prop(value, '$value');
    if (typedValue !== undefined && (prop(value, '$type') !== undefined || prop(value, '$storage') !== undefined)) {
        return compact(typedValue, limit);
    }
    let text;
    try {
        text = JSON.stringify(value);
    } catch (e) {
        text = String(value);
    }
    if (text.length > limit) return text.slice(0, limit) + '…';
    return text;
}

function typeName(value) {
    const obj = unwrap(value);
    const type = prop(obj, '$type');
    if (type !== undefined) return String(compact(type));
    return '';
}

function readSelectedFields(node) {
    const result = [];
    const visited = new Set();

    function walk(value, path, depth) {
        if (depth > 12 || value === null || value === undefined || typeof value !== 'object') return;
        if (Array.isArray(value)) {
            value.forEach((item, index) => walk(item, path + '[' + index + ']', depth + 1));
            return;
        }
        if (visited.has(value)) return;
        visited.add(value);
        for (const key of Object.keys(value)) {
            const nextPath = path ? path + '.' + key : key;
            const child = value[key];
            if (INTERESTING_FIELDS.has(key.toLowerCase())) {
                result.push({ field: nextPath, value: compact(child) });
            }
            walk(child, nextPath, depth + 1);
        }
    }

    walk(node, '', 0);
    return result;
}

function readSockets(node) {
    const rawSockets = prop(unwrap(node), 'sockets');
    if (!Array.isArray(rawSockets)) return [];
    return rawSockets.map((rawSocket, socketIndex) => {
        const socket = unwrap(rawSocket);
        const rawConnections = prop(socket, 'connections');
        const connections = Array.isArray(rawConnections) ? rawConnections.map(rawConnection => {
            const connection = unwrap(rawConnection);
            return { destination: compact(prop(connection, 'destination'), 500) };
        }) : [];
        return {
            index: socketIndex,
            name: compact(prop(socket, 'name')),
            type: compact(prop(socket, 'type')),
            connections: connections
        };
    });
}

function collectNodes(value, path, found, depth) {
    if (depth > 80 || value === null || value === undefined || typeof value !== 'object') return;
    if (Array.isArray(value)) {
        value.forEach((item, index) => collectNodes(item, path + '[' + index + ']', found, depth + 1));
        return;
    }

    const obj = unwrap(value);
    const type = typeName(obj);
    const id = prop(obj, 'id');
    const sockets = prop(obj, 'sockets');
    const looksLikeNode = /(?:NodeDefinition|Node)$/i.test(type) &&
        (id !== undefined || Array.isArray(sockets));

    if (looksLikeNode) {
        const idText = compact(id);
        const key = type + '|' + String(idText) + '|' + path;
        if (!found.some(item => item._key === key)) {
            found.push({
                _key: key,
                id: idText,
                type: type,
                fields: readSelectedFields(obj),
                sockets: readSockets(obj),
                jsonPath: path
            });
        }
    }

    for (const key of Object.keys(obj)) {
        if (key === '$type') continue;
        collectNodes(obj[key], path ? path + '.' + key : key, found, depth + 1);
    }
}

Logger.Info('=== Q003 read-only metadata report. No vanilla resource files are written. ===');
Logger.Info('WolvenKit version: ' + wkit.ProgramVersion());

for (const resourcePath of RESOURCE_PATHS) {
    const jsonText = wkit.GetFileFromArchive(resourcePath, OpenAs.Json);
    if (jsonText === null || jsonText === undefined) {
        Logger.Warning(JSON.stringify({ resource: resourcePath, status: 'not found in mounted archives' }));
        continue;
    }

    let parsed;
    try {
        parsed = typeof jsonText === 'string' ? JSON.parse(jsonText) : jsonText;
    } catch (e) {
        Logger.Error(JSON.stringify({ resource: resourcePath, status: 'could not parse in-memory JSON', error: String(e) }));
        continue;
    }

    const nodes = [];
    collectNodes(parsed, '$', nodes, 0);
    const report = nodes.map(item => {
        const copy = Object.assign({}, item);
        delete copy._key;
        return copy;
    });

    Logger.Info(JSON.stringify({ resource: resourcePath, status: 'read in memory', nodeCount: report.length }));
    report.forEach(item => Logger.Info(JSON.stringify(item)));
}

Logger.Info('=== End of Q003 report ===');

