#!/usr/bin/env node

import { syncClawhub } from './lib/sync-helpers.mjs';

const args = process.argv.slice(2);
const options = {
    root: process.cwd(),
    dryRun: false,
    all: false,
    skills: [],
};

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--dry-run') {
        options.dryRun = true;
    } else if (arg === '--all') {
        options.all = true;
    } else if (arg === '--root' && args[i + 1]) {
        options.root = args[++i];
    } else if (!arg.startsWith('--')) {
        options.skills.push(arg);
    }
}

if (options.all && options.skills.length > 0) {
    console.error('Error: --all and specific skills cannot be used together');
    process.exit(1);
}

await syncClawhub(options);
