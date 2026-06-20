use std::fs;
use std::io;

use crate::paths::temp_dir;

pub(super) fn get_origin_cache() -> Result<String, io::Error> {
    fs::read_to_string(temp_dir().join("origin.ftml"))
}
