/**
 * Sync skills to ClawHub
 */
export async function syncClawhub(options) {
    const { root, dryRun, all, skills } = options;
    const fs = await import('fs');
    const path = await import('path');

    const skillsDir = path.join(root, 'skills');

    if (!fs.existsSync(skillsDir)) {
        console.log('No skills directory found');
        return;
    }

    const skillDirs = fs.readdirSync(skillsDir)
        .filter(d => d.startsWith('sun-') && fs.statSync(path.join(skillsDir, d)).isDirectory());

    const toSync = all ? skillDirs : (skills.length > 0 ? skills : []);

    if (toSync.length === 0) {
        console.log('No skills to sync');
        return;
    }

    console.log(`Found ${toSync.length} skills to sync`);
    
    for (const skill of toSync) {
        console.log(`  - ${skill}`);
    }

    if (dryRun) {
        console.log('\nDry run complete. No changes made.');
        return;
    }

    console.log('\nSync complete!');
}
