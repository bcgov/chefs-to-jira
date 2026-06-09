/**
 * Cryptr decryption helper
 * Called from Python
 */

const Cryptr = require('cryptr');

const key = process.argv[2];
const encrypted = process.argv[3];

if (!key || !encrypted) {
    console.error("DECRYPT_ERROR: Missing key or payload");
    process.exit(1);
}

try {
    const cryptr = new Cryptr(key);
    const decrypted = cryptr.decrypt(encrypted);
    console.log(decrypted);
} catch (err) {
    console.error("DECRYPT_ERROR:" + err.message);
    process.exit(2);
}