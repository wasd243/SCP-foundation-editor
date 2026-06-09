use std::fs;
use std::io;

const ORIGIN_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/origin.ftml");

pub(super) fn get_origin_cache() -> Result<String, io::Error> {
    fs::read_to_string(ORIGIN_PATH)
}
