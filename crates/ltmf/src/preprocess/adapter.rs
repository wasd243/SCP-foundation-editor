mod image_block;

use serde_json::Value;

use crate::preprocess::adapter::image_block::adapt_image_block;

pub fn pm_json_reverse_adapter(value: Value) -> Value {
    adapt_image_block(value)
}

