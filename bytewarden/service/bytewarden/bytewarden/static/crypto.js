
// Inspired by https://balsn.tw/proof-of-work/solver/js.html
function findMatching(prefix, difficulty) {

	let zeros = "0".repeat(difficulty);

	let isValid = (hexdigest) => {
		let bin = '';
		for (let c of hexdigest){
			bin += parseInt(c, 16).toString(2).padStart(4, "0"); 
		}
		return bin.startsWith(zeros);
	}
	
	for(let i = 0; true; i++) {
		let hexdigest = sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(prefix + i.toString()));
		if (isValid(hexdigest)){
			return i;
		}
	}
}


function compute_pow(form_name){

	const form = document.forms[form_name];
	const prefix = form.elements["prefix"].value;
	const difficulty = form.elements["difficulty"].value; 

	form.elements["pow"].value = findMatching(prefix, difficulty);

	if (form.reportValidity()){
		form.submit();
	}
}


function encrypt_id(plaintext, password, id){
	document.getElementById(id).innerHTML = encrypt(password, plaintext);
}

function decrypt_id(data, password, id){
	document.getElementById(id).innerHTML = decrypt(password, data);
}

function submit_form(form_name, password){
	form = document.forms[form_name];
	form_elements = form.elements;

	for (i = 0; i < form_elements.length; i++) {
		el = form_elements[i];
		if((el.type === "text" || el.type === "password") && el.name !== "username"){
			el.value = encrypt(password, el.value);
		}
	}

	if (form.reportValidity()){
		form.submit();
	}
}

function XOR_hex(password, data) {
	let res = "";
	for (let i = 0; i < data.length; i++) {
		const xor = password.charCodeAt(i % password.length) ^ data.charCodeAt(i);
		res += String.fromCharCode(xor);
	}
	return res;
}

function encrypt(password, plaintext){
	console.log(XOR_hex(password, plaintext))
	return btoa(XOR_hex(password, plaintext));
}

function decrypt(password, data){
	return XOR_hex(password, atob(data));
}
