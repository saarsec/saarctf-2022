use sha2::{Sha256, Digest};

fn to_hex_string(bytes: Vec<u8>) -> String {
    let strs: Vec<String> = bytes.iter().map(|b| format!("{:02x}", b)).collect();
    strs.join("")
}

pub fn get_hash(input: String) -> String {
    let mut hasher = Sha256::new();
    hasher.update(input);
    let result = hasher.finalize();
    let mut vec_result = Vec::new();
    for b in result {
        vec_result.push(b);
    }
    to_hex_string(vec_result)
}