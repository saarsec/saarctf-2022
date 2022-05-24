use std::{env, fs, io::Write, io::Read, path::Path};

/// Write comment to file. If it exists, append and separate by ,
pub fn write_personal_comment(email_hash: String, comment: String) -> Result<(), std::io::Error> {
    let comment = comment.replace(',', ";");
    let comment = comment + ",";
    let file = "data/users/".to_string() + &email_hash;
    let mut path = env::current_dir()?;
    path.push("data/");
    path.push("users/");
    let dir_metadata = fs::metadata(&path);
    if dir_metadata.is_err() {
        fs::create_dir_all(path).expect("Could not create directory!");
    }

    let filepath = Path::new(&file);
    let metadata = fs::metadata(&filepath);
    match metadata {
        Ok(metadata) => {
            if metadata.is_file() {
                let mut fd = fs::OpenOptions::new()
                    .write(true)
                    .append(true)
                    .create(true)
                    .open(file)?;
                fd.write_all(comment.as_bytes())?;
            }
        }
        Err(e) => {
            if e.kind() == std::io::ErrorKind::NotFound {
                let mut fd = fs::OpenOptions::new()
                    .write(true)
                    .append(true)
                    .create(true)
                    .open(file)?;
                fd.write_all(comment.as_bytes())?;
            }
            println!("{:#?}", e);
        }
    }

    Ok(())
}

/// Write comment to file. If it exists, append and separate by ,
pub fn write_rating(stop: String, comment: String) -> Result<(), std::io::Error> {
    let comment = comment.replace(',', ";");
    let comment = comment + ",";
    let file = "data/stops/".to_string() + &stop;
    let mut path = env::current_dir()?;
    path.push("data/");
    path.push("stops/");
    let dir_metadata = fs::metadata(&path);
    if dir_metadata.is_err() {
        fs::create_dir_all(path).expect("Could not create directory!");
    }

    let filepath = Path::new(&file);
    let metadata = fs::metadata(&filepath);
    match metadata {
        Ok(metadata) => {
            if metadata.is_file() {
                let mut fd = fs::OpenOptions::new()
                    .write(true)
                    .append(true)
                    .create(true)
                    .open(file)?;
                fd.write_all(comment.as_bytes())?;
            }
        }
        Err(e) => {
            if e.kind() == std::io::ErrorKind::NotFound {
                let mut fd = fs::OpenOptions::new()
                    .write(true)
                    .append(true)
                    .create(true)
                    .open(file)?;
                fd.write_all(comment.as_bytes())?;
            }
            println!("{:#?}", e);
        }
    }
    Ok(())
}

pub fn get_personal_comments(email_hash: String) -> Vec<String> {
    let mut path = env::current_dir().expect("Could not read current directory!");
    path.push("data/users/");
    path.push(email_hash);
    let metadata = fs::metadata(&path);
    

    match metadata {
        Ok(metadata) => {
            if metadata.is_file() {
                let mut fd = fs::OpenOptions::new()
                    .read(true)
                    .open(path)
                    .expect("Could not open file!");
                let mut contents = String::new();
                fd.read_to_string(&mut contents).expect("Could not read file!");
                let mut comments = contents.split(',');
                let mut result = Vec::new();
                for comment in comments {
                    if !comment.is_empty() {
                        result.push(comment.to_string());
                    }
                }
                return result;
            }
            else {
                panic!("File is not a file!");
            }
        }
        Err(e) => {
            println!("{:#?}", e);
            return Vec::new();
        }
    }
}

pub fn get_ratings(stop: String) -> Vec<String> {
    let mut path = env::current_dir().expect("Could not read current directory!");
    path.push("data/stops/");
    path.push(stop);
    let metadata = fs::metadata(&path);

    match metadata {
        Ok(metadata) => {
            if metadata.is_file() {
                let mut fd = fs::OpenOptions::new()
                    .read(true)
                    .open(path)
                    .expect("Could not open file!");
                let mut contents = String::new();
                fd.read_to_string(&mut contents).expect("Could not read file!");
                let mut comments = contents.split(',');
                let mut result = Vec::new();
                for comment in comments {
                    if !comment.is_empty() {
                        result.push(comment.to_string());
                    }
                }
                return result;
            }
            else {
                panic!("Not a file!");
            }
        }
        Err(e) => {
            println!("{:#?}", e);
            return Vec::new();
        }
    }
}