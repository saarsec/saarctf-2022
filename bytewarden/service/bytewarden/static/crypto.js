
// Inspired by https://balsn.tw/proof-of-work/solver/js.html
async function findMatching(prefix, difficulty) {

    let zeros = '0'.repeat(difficulty);

    let isValid = (hexdigest) => {
        let bin = '';
        for (let c of hexdigest){
            bin += parseInt(c, 16).toString(2).padStart(4, '0'); 
        }
        return bin.startsWith(zeros);
    }
    
    for(let i = 0; true; i++) {
        const buf = await crypto.subtle.digest("SHA-256", new TextEncoder("utf-8").encode(prefix + i.toString()));
        const hexdigest = Array.prototype.map.call(new Uint8Array(buf), x=>(('00'+x.toString(16)).slice(-2))).join('');
        if (isValid(hexdigest)){
            return i;
        }
    }
}


async function compute_pow(form_name){

    const form = document.forms[form_name]
    const prefix = form.elements["prefix"].value;
    const difficulty = form.elements["difficulty"].value; 

    form.elements["pow"].value = await findMatching(prefix, difficulty)

    if (form.reportValidity()){
        form.submit()
    }
}


async function encrypt_id(plaintext, key, id){
	document.getElementById(id).innerHTML = await aesGcmEncrypt(plaintext, key)
}

async function decrypt_id(ciphertext, key, id){
	document.getElementById(id).innerHTML = await aesGcmDecrypt(ciphertext, key)
}

async function submit_form(form_name, key){
	form = document.forms[form_name]
	form_elements = form.elements

	for (i = 0; i < form_elements.length; i++) {
        el = form_elements[i]
		if((el.type === "text" || el.type === "password") && el.name !== "username"){
			el.value = await aesGcmEncrypt(el.value, key)
		}
	}

    if (form.reportValidity()){
        form.submit()
    }
}

/**
 * Encrypts plaintext using AES-GCM with supplied password, for decryption with aesGcmDecrypt().
 *                                                                      (c) Chris Veness MIT Licence
 *
 * @param   {String} plaintext - Plaintext to be encrypted.
 * @param   {String} password - Password to use to encrypt plaintext.
 * @returns {String} Encrypted ciphertext.
 *
 * @example
 *   const ciphertext = await aesGcmEncrypt('my secret text', 'pw');
 *   aesGcmEncrypt('my secret text', 'pw').then(function(ciphertext) { console.log(ciphertext); });
 */
async function aesGcmEncrypt(plaintext, password) {

    const pwUtf8 = new TextEncoder().encode(password);                                 // encode password as UTF-8
    const pwHash = await crypto.subtle.digest('SHA-256', pwUtf8);                      // hash the password
    
    const iv = new Uint8Array(12).fill(0);//crypto.getRandomValues(new Uint8Array(12));                             // get 96-bit random iv
    const ivStr = Array.from(iv).map(b => String.fromCharCode(b)).join('');            // iv as utf-8 string
    const alg = { name: 'AES-GCM', iv: iv };                                           // specify algorithm to use

    const key = await crypto.subtle.importKey('raw', pwHash, alg, false, ['encrypt']); // generate key from pw

    const ptUint8 = new TextEncoder().encode(plaintext);                               // encode plaintext as UTF-8
    const ctBuffer = await crypto.subtle.encrypt(alg, key, ptUint8);                   // encrypt plaintext using key

    const ctArray = Array.from(new Uint8Array(ctBuffer));                              // ciphertext as byte array
    const ctStr = ctArray.map(byte => String.fromCharCode(byte)).join('');             // ciphertext as string

    return btoa(ivStr+ctStr);                                                          // iv+ciphertext base64-encoded
}


/**
 * Decrypts ciphertext encrypted with aesGcmEncrypt() using supplied password.
 *                                                                      (c) Chris Veness MIT Licence
 *
 * @param   {String} ciphertext - Ciphertext to be decrypted.
 * @param   {String} password - Password to use to decrypt ciphertext.
 * @returns {String} Decrypted plaintext.
 *
 * @example
 *   const plaintext = await aesGcmDecrypt(ciphertext, 'pw');
 *   aesGcmDecrypt(ciphertext, 'pw').then(function(plaintext) { console.log(plaintext); });
 */
async function aesGcmDecrypt(ciphertext, password) { 
    
    const pwUtf8 = new TextEncoder().encode(password);                                 // encode password as UTF-8
    const pwHash = await crypto.subtle.digest('SHA-256', pwUtf8);                      // hash the password

    const ivStr = atob(ciphertext).slice(0,12);                                        // decode base64 iv
    const iv = new Uint8Array(Array.from(ivStr).map(ch => ch.charCodeAt(0)));          // iv as Uint8Array

    const alg = { name: 'AES-GCM', iv: iv };                                           // specify algorithm to use

    const key = await crypto.subtle.importKey('raw', pwHash, alg, false, ['decrypt']); // generate key from pw

    const ctStr = atob(ciphertext).slice(12);                                          // decode base64 ciphertext
    const ctUint8 = new Uint8Array(Array.from(ctStr).map(ch => ch.charCodeAt(0)));     // ciphertext as Uint8Array

    try {
        const plainBuffer = await crypto.subtle.decrypt(alg, key, ctUint8);            // decrypt ciphertext using key
        const plaintext = new TextDecoder().decode(plainBuffer);                       // plaintext from ArrayBuffer
        return plaintext;                                                              // return the plaintext
    } catch (e) {
        throw new Error('Decrypt failed');
    }
}
