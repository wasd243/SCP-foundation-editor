mod text;
mod wiki_component;
mod include;

pub fn identify(json: &str) -> Result<String, String> {
    println!("{}", json);

    Ok(json.to_string())
}
