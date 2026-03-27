/**
 * Publish a skill to npm/ClawHub
 */
const args = process.argv.slice(2);

if (args.length === 0) {
    console.error('Usage: node publish-skill.mjs <skill-name>');
    process.exit(1);
}

const skillName = args[0];

if (!skillName.startsWith('sun-')) {
    console.error('Skill name must start with "sun-"');
    process.exit(1);
}

console.log(`Publishing ${skillName}...`);
// Placeholder for actual publishing logic
